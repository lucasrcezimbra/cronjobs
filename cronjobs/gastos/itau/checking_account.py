from datetime import date, datetime
from typing import Optional

from attrs import define
from cattrs import Converter

from cronjobs.gastos.sheet import Row

converter = Converter()
converter.register_structure_hook(
    date, lambda v, _: datetime.strptime(v, "%d/%m/%Y").date() if v else None
)


def data_to_rows(data, date_):
    for entry_data in data["lancamentos"]:
        entry = converter.structure(entry_data, Entry)
        if entry.indicadorOperacao not in ("credito", "debito"):
            continue
        if entry.dataLancamento < date_:
            continue
        yield entry.to_row()


@define
class Entry:
    dataLancamento: Optional[date]
    descricaoLancamento: str
    descricaoDetalhadaLancamento: str
    valorLancamento: str
    indicadorOperacao: str

    def to_row(self):
        return Row(
            date_=str(self.dataLancamento),
            description=self.description,
            bank="Itaú Conta",
            business_raw=self.description,
            value=self.value,
        )

    @property
    def description(self):
        # TODO: remove date from description
        return self.descricaoDetalhadaLancamento or self.descricaoLancamento

    @property
    def value(self):
        value = self.valorLancamento
        if self.indicadorOperacao == "debito":
            value = f"-{value}"
        return value
