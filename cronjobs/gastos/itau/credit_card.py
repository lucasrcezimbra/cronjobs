import re
from datetime import date
from decimal import Decimal

from attrs import define
from cattrs import Converter

from cronjobs.gastos.sheet import Row

converter = Converter()
converter.register_structure_hook(
    date, lambda v, _: date.fromisoformat(v) if v else None
)
converter.register_structure_hook(
    Decimal, lambda v, _: Decimal(v.replace(".", "").replace(",", ".")) if v else None
)


def data_to_rows(invoices_data, month):
    entries_data = []

    def extend(data):
        if not data:
            return

        for t in data["titularidades"]:
            entries_data.extend(t["lancamentos"])

    for d in invoices_data["object"]["faturas"]:
        if date.fromisoformat(d["dataVencimento"]).month != month:
            continue

        # TODO: drop events after date_.day
        extend(d.get("lancamentosNacionais"))
        extend(d.get("lancamentosInternacionais"))
        extend(d.get("comprasParceladas"))

    return [converter.structure(d, Entry).to_row() for d in entries_data]


@define
class Entry:
    # TODO: translate to english
    data: date
    descricao: str
    valor: Decimal
    sinalValor: str

    def to_row(self):
        return Row(
            date_=self.data,
            description=self.descricao,
            bank="Itaú Crédito",
            business_raw=self.business,
            installment=self.installment,
            value=-self.valor,
        )

    @property
    def business(self):
        return self._business_and_installment(self.descricao)[0]

    @property
    def installment(self):
        return self._business_and_installment(self.descricao)[1]

    @staticmethod
    def _business_and_installment(description):
        search = re.search(r"\(?([0-9]{1,2}\/[0-9]{1,2})\)?", description)

        if not search:
            return description.strip(), ""

        business = description.replace(search.group(0), "").strip()
        installment = search.group(1)
        return business, installment
