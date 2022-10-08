from datetime import date
from uuid import uuid4

import pytest

from nubank_spreadsheet import __create_dataframe

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
            'detail': 'Jesse Pinkman - R$\xa040,50',
            'postDate': date_.strftime('%Y-%m-%d'),
            'amount': 40.5,
        },
        {
            'id': uuid4(),
            '__typename': 'TransferOutEvent',
            'title': 'Transferência enviada',
            'detail': 'Walter White - R$\xa0126,88',
            'postDate': date_.strftime('%Y-%m-%d'),
            'amount': 126.88,
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


def test_debit_lenght(debit_events):
    dataframe = __create_dataframe([], debit_events, date_)
    assert len(dataframe) == len(debit_events)


def test_debit_transfer_in(debit_events):
    dataframe = __create_dataframe([], debit_events, date_)

    records = dataframe.to_records(index=False)
    event = debit_events[TRANSFER_IN_EVENT_INDEX]
    result = records[TRANSFER_IN_EVENT_INDEX]
    row = TRANSFER_IN_EVENT_INDEX + 2

    assert result[0] == event['postDate']
    assert result[1] == f'=VLOOKUP(G{row};Categorias!F:G;2;FALSE)'
    assert result[2] == ''
    assert result[3] == event['title']
    assert result[4] == 'NuConta'
    assert result[5] == event['detail']
    assert result[6] == f'=VLOOKUP(F{row};Categorias!E:F;2;FALSE)'
    assert result[7] is None
    assert result[8] == event['amount']
    assert result[9] == ''
    assert result[10] == f'=I{row}+J{row}'


def test_debit_transfer_out(debit_events):
    dataframe = __create_dataframe([], debit_events, date_)

    records = dataframe.to_records(index=False)
    event = debit_events[TRANSFER_OUT_EVENT_INDEX]
    result = records[TRANSFER_OUT_EVENT_INDEX]
    row = TRANSFER_OUT_EVENT_INDEX + 2

    assert result[0] == event['postDate']
    assert result[1] == f'=VLOOKUP(G{row};Categorias!F:G;2;FALSE)'
    assert result[2] == ''
    assert result[3] == event['title']
    assert result[4] == 'NuConta'
    assert result[5] == event['detail']
    assert result[6] == f'=VLOOKUP(F{row};Categorias!E:F;2;FALSE)'
    assert result[7] is None
    assert result[8] == (event['amount'] * -1)
    assert result[9] == ''
    assert result[10] == f'=I{row}+J{row}'


def test_debit_pix_transfer_out(debit_events):
    dataframe = __create_dataframe([], debit_events, date_)

    records = dataframe.to_records(index=False)
    event = debit_events[PIX_OUT_EVENT_INDEX]
    result = records[PIX_OUT_EVENT_INDEX]
    row = PIX_OUT_EVENT_INDEX + 2

    assert result[0] == event['postDate']
    assert result[1] == f'=VLOOKUP(G{row};Categorias!F:G;2;FALSE)'
    assert result[2] == ''
    assert result[3] == event['title']
    assert result[4] == 'NuConta'
    assert result[5] == event['detail']
    assert result[6] == f'=VLOOKUP(F{row};Categorias!E:F;2;FALSE)'
    assert result[7] is None
    assert result[8] == (event['amount'] * -1)
    assert result[9] == ''
    assert result[10] == f'=I{row}+J{row}'
