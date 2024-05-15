from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from attrs import define
from cattrs import Converter
from loguru import logger

from cronjobs.storage.google.sheet import Worksheet

converter = Converter()
converter.register_unstructure_hook(date, lambda d: d.strftime("%d/%m/%Y"))
converter.register_structure_hook(
    date, lambda d, _: datetime.strptime(d, "%d/%m/%Y").date() if d else None
)
converter.register_unstructure_hook(Decimal, lambda d: str(d).replace(".", ","))
converter.register_structure_hook(
    Decimal,
    lambda d, _: Decimal(d.replace("R$ ", "").replace(".", "").replace(",", "."))
    if d
    else None,
)


class Cell(str):
    pass


@define
class Row:
    date_: Optional[date] = None
    categoria: Cell = Cell("=VLOOKUP(G{n};_Categorias!F:G;2;FALSE)")
    recurrent: Optional[str] = ""
    description: str = ""
    bank: str = ""
    business_raw: str = ""
    business: Cell = Cell("=VLOOKUP(F{n};_Categorias!E:F;2;FALSE)")
    installment: Optional[str] = ""
    value: Decimal = ""
    new: str = "NEW"

    def format(self, n=None, index=None):
        n = n if n else index + 2
        self.categoria = self.categoria.format(n=n)
        self.business = self.business.format(n=n)
        return self

    def __eq__(self, other):
        return (
            self.date_ == other.date_
            and self.recurrent == other.recurrent
            and self.bank == other.bank
            and self.business_raw == other.business_raw
            and self.installment == other.installment
            and self.value == other.value
        )


MONTHS = [
    "",
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
]


def deduplicate(rows, existing_rows):
    logger.info(f"Deduplicating {len(rows)} rows against {len(existing_rows)} existing")
    result = [r for r in rows if r not in existing_rows]
    logger.info(f"{len(result)} rows left after deduplication")
    return result


def insert(rows, date_, deduplicate=deduplicate):
    if not rows:
        return

    worksheet = Worksheet(
        name=MONTHS[date_.month], spreadsheet_name=f"Gastos {date_.year}"
    )

    if deduplicate:
        existing_rows = [
            converter.structure_attrs_fromtuple(r, Row) for r in worksheet.get_all()[1:]
        ]
        rows = deduplicate(rows, existing_rows)

    values = [
        list(converter.unstructure_attrs_astuple(r.format(index=i)))
        for i, r in enumerate(rows)
    ]
    worksheet.insert(values)
