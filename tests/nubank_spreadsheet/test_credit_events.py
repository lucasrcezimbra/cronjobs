from datetime import datetime
from uuid import uuid4

import pytest

from nubank_spreadsheet import get_rows

datetime_ = datetime(2021, 9, 4, 16, 28, 21)


@pytest.fixture
def credit_events():
    return [
        {
            'description': 'Ifood *Ifood',
            'category': 'transaction',
            'amount': 4321,
            'time': datetime_.isoformat() + 'Z',
            'source': 'upfront_national',
            'title': 'restaurante',
            'amount_without_iof': 4321,
            'account': uuid4(),
            'details': {
                'status': 'unsettled',
                'subcategory': 'card_not_present'
            },
            'id': uuid4(),
            '_links': {
                'self': {
                    'href': f'https://prod-s0-facade.nubank.com.br/api/transactions/{uuid4()}',
                }
            },
            'tokenized': False,
            'href': f'nuapp://transaction/{uuid4()}'
        },
    ]


def test_lenght(credit_events):
    rows = get_rows(credit_events, [], datetime_.date())
    assert len(rows) == len(credit_events)


def test_nubank_transaction(credit_events):
    rows = get_rows(credit_events, [], datetime_.date())

    index = 0
    event = credit_events[index]
    row = rows[index]
    row_index = index + 2

    assert row == [
        datetime.fromisoformat(event['time'][:-1]).date().strftime('%Y-%m-%d'),
        f'=VLOOKUP(F{row_index};Categorias!F:G;2;FALSE)',
        None,
        'NuBank',
        event['description'],
        f'=VLOOKUP(E{row_index};Categorias!E:F;2;FALSE)',
        '',
        (int(event['amount']) / -100),
        None,
        f'=H{row_index}+I{row_index}',
    ]
