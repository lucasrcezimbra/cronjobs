from typing import Optional

from attrs import define
from cattrs import Converter

from cronjobs.storage.google import sheet

converter = Converter()


@define
class Row:
    date_: str
    categoria: Optional[str] = ''
    recurrent: Optional[str] = ''
    description: str = ''
    bank: str = ''
    business_raw: str = ''
    business: Optional[str] = ''
    installment: Optional[str] = ''
    value: str = ''


MONTHS = [
    '',
    'Jan', 'Fev', 'Mar', 'Abr', 'Maio', 'Jun',
    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
]


def insert(rows, date_):
    if not rows:
        return

    values = [list(converter.unstructure_attrs_astuple(r)) for r in rows]
    sheet.insert(f'Gastos {date_.year}', MONTHS[date_.month], values)
