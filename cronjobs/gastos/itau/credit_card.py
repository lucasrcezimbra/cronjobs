import re
from datetime import date

from attrs import define
from cattrs import Converter

from cronjobs.gastos.sheet import Row

converter = Converter()


def data_to_rows(invoices_data, month):
    entries_data = []

    def extend(data):
        if not data:
            return

        print(f"Appending {len(data['titularidades'])} lançamentos nacionais")
        for t in data["titularidades"]:
            entries_data.extend(t["lancamentos"])

    for d in invoices_data["object"]["faturas"]:
        if date.fromisoformat(d["dataVencimento"]).month != month:
            print(f"Skipping {d['dataVencimento']}")
            continue

        print(f"Running for {d['dataVencimento']}")
        extend(d["lancamentosNacionais"])
        extend(d["lancamentosInternacionais"])
        extend(d["comprasParceladas"])

    return [converter.structure(d, Entry).to_row() for d in entries_data]


@define
class Entry:
    # TODO: translate to english
    data: str
    descricao: str
    valor: str
    sinalValor: str

    def to_row(self):
        return Row(
            date_=self.data,
            description=self.descricao,
            bank="Itaú Crédito",
            business_raw=self.business,
            installment=self.installment,
            value=f"-{self.valor}",
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
            return description.strip(), None

        business = description.replace(search.group(0), "").strip()
        installment = search.group(1)
        return business, installment
