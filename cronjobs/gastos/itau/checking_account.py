import re
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from attrs import define
from cattrs import Converter
from loguru import logger

from cronjobs.gastos.sheet import Row

converter = Converter()
converter.register_structure_hook(
    date, lambda v, _: datetime.strptime(v, "%d/%m/%Y").date() if v else None
)
converter.register_structure_hook(
    Decimal, lambda v, _: Decimal(v.replace(".", "").replace(",", ".")) if v else None
)


def data_to_rows(data, date_):
    entries_data = data["lancamentos"]

    if not entries_data:
        logger.warning(f'No entries found for date "{date_}"')
        return

    for entry_data in entries_data:
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
    valorLancamento: Decimal
    indicadorOperacao: str

    def to_row(self):
        return Row(
            date_=self.dataLancamento,
            description=self.description,
            bank="Itaú Conta",
            business_raw=self.description,
            value=self.value,
        )

    @property
    def description(self):
        return re.sub(r"(\d{2}/\d{2})", "", self.descricaoLancamento).strip()

    @property
    def value(self):
        value = self.valorLancamento
        if self.indicadorOperacao == "debito":
            value = -value
        return value
