from typing import Optional

from attrs import define
from cattrs import Converter

from cronjobs.storage.google.sheet import Worksheet

converter = Converter()


@define
class Row:
    date_: str
    categoria: Optional[str] = ""
    recurrent: Optional[str] = ""
    description: str = ""
    bank: str = ""
    business_raw: str = ""
    business: Optional[str] = ""
    installment: Optional[str] = ""
    value: str = ""
    new: str = "NEW"

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
    "Maio",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
]


def deduplicate(rows, existing_rows):
    return [r for r in rows if r not in existing_rows]


def insert(rows, date_, deduplicate=deduplicate):
    if not rows:
        return

    worksheet = Worksheet(f"Gastos {date_.year}", MONTHS[date_.month])

    if deduplicate:
        existing_rows = [
            converter.structure_attrs_fromtuple(r, Row) for r in worksheet.get_all()
        ]
        rows = deduplicate(rows, existing_rows)

    values = [list(converter.unstructure_attrs_astuple(r)) for r in rows]
    worksheet.insert(values)
