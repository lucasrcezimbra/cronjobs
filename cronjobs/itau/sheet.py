from typing import Optional

from attrs import define

from cronjobs.storage.google import sheet


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


def insert(rows, month):
    if not rows:
        return

    # TODO: remove hardcoded spreadsheet name
    sheet.insert('Gastos 2023', MONTHS[month], rows)
