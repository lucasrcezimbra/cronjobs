from datetime import date
from uuid import uuid4

import pytest

from nubank_spreadsheet import get_rows

date_ = date(2021, 8, 25)


TRANSFER_IN_EVENT_INDEX = 0
TRANSFER_OUT_EVENT_INDEX = 1
PIX_OUT_EVENT_INDEX = 2


@pytest.fixture
def debit_events():
    return [
        {
            'id': uuid4(),
            '__typename': 'TransferInEvent',
            'title': 'Transferência recebida',
            'detail': 'R$\xa040,50',
            'postDate': date_.strftime('%Y-%m-%d'),
            'amount': 40.5,
            'originAccount': {'name': 'Jesse Pinkman'}
        },
        {
            'id': uuid4(),
            '__typename': 'TransferOutEvent',
            'title': 'Transferência enviada',
            'detail': 'Walter White - R$\xa0126,88',
            'postDate': date_.strftime('%Y-%m-%d'),
            'amount': 126.88,
            'destinationAccount': {'name': 'Walter White'},
        },
        {
            'id': uuid4(),
            '__typename': 'PixTransferOutEvent',
            'title': 'Transferência enviada',
            'detail': 'Saul Goodman\nR$\xa0600,00',
            'postDate': date_.strftime('%Y-%m-%d'),
            'amount': 600.0,
        },
    ]


def test_lenght(debit_events):
    rows = get_rows([], debit_events, date_)
    assert len(rows) == len(debit_events)


def test_debit_transfer_in(debit_events):
    rows = get_rows([], debit_events, date_)

    event = debit_events[TRANSFER_IN_EVENT_INDEX]
    rows = rows[TRANSFER_IN_EVENT_INDEX]
    row_index = TRANSFER_IN_EVENT_INDEX + 2

    assert rows == [
        event['postDate'],
        f'=VLOOKUP(F{row_index};Categorias!F:G;2;FALSE)',
        event['title'],
        'NuConta',
        event['originAccount']['name'],
        f'=VLOOKUP(E{row_index};Categorias!E:F;2;FALSE)',
        None,
        event['amount'],
        '',
        f'=H{row_index}+I{row_index}',
    ]


def test_debit_transfer_out(debit_events):
    rows = get_rows([], debit_events, date_)

    event = debit_events[TRANSFER_OUT_EVENT_INDEX]
    row = rows[TRANSFER_OUT_EVENT_INDEX]
    row_index = TRANSFER_OUT_EVENT_INDEX + 2

    assert row == [
        event['postDate'],
        f'=VLOOKUP(F{row_index};Categorias!F:G;2;FALSE)',
        event['title'],
        'NuConta',
        event['destinationAccount']['name'],
        f'=VLOOKUP(E{row_index};Categorias!E:F;2;FALSE)',
        None,
        (event['amount'] * -1),
        '',
        f'=H{row_index}+I{row_index}',
    ]


def test_debit_pix_transfer_out(debit_events):
    rows = get_rows([], debit_events, date_)

    event = debit_events[PIX_OUT_EVENT_INDEX]
    row = rows[PIX_OUT_EVENT_INDEX]
    row_index = PIX_OUT_EVENT_INDEX + 2

    assert row == [
        event['postDate'],
        f'=VLOOKUP(F{row_index};Categorias!F:G;2;FALSE)',
        event['title'],
        'NuConta',
        event['detail'],
        f'=VLOOKUP(E{row_index};Categorias!E:F;2;FALSE)',
        None,
        (event['amount'] * -1),
        '',
        f'=H{row_index}+I{row_index}',
    ]
