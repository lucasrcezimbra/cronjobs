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
    ]


def test_debit_transfer_in(debit_events):
    dataframe = __create_dataframe([], debit_events, date_)

    assert len(dataframe) == len(debit_events)

    records = dataframe.to_records(index=False)
    event = debit_events[TRANSFER_IN_EVENT_INDEX]
    result = records[TRANSFER_IN_EVENT_INDEX]
    row = TRANSFER_IN_EVENT_INDEX + 2

    assert result[0] == event['postDate']
    assert result[1] == f'=VLOOKUP(F{row};Categorias!F:G;2;FALSE)'
    assert result[2] == 'Transferência recebida'
    assert result[3] == 'NuConta'
    assert result[4] == event['originAccount']['name']
    assert result[5] == f'=VLOOKUP(E{row};Categorias!E:F;2;FALSE)'
    assert result[6] is None
    assert result[7] == event['amount']
    assert result[8] == ''
    assert result[9] == f'=H{row}+I{row}'


def test_debit_transfer_out(debit_events):
    dataframe = __create_dataframe([], debit_events, date_)

    assert len(dataframe) == len(debit_events)

    records = dataframe.to_records(index=False)
    event = debit_events[TRANSFER_OUT_EVENT_INDEX]
    result = records[TRANSFER_OUT_EVENT_INDEX]
    row = TRANSFER_OUT_EVENT_INDEX + 2

    assert result[0] == event['postDate']
    assert result[1] == f'=VLOOKUP(F{row};Categorias!F:G;2;FALSE)'
    assert result[2] == 'Transferência enviada'
    assert result[3] == 'NuConta'
    assert result[4] == event['destinationAccount']['name']
    assert result[5] == f'=VLOOKUP(E{row};Categorias!E:F;2;FALSE)'
    assert result[6] is None
    assert result[7] == (event['amount'] * -1)
    assert result[8] == ''
    assert result[9] == f'=H{row}+I{row}'
