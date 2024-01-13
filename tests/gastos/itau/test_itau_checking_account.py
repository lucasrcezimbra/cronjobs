from decimal import Decimal

import pytest

from cronjobs.gastos.itau.checking_account import Entry


@pytest.mark.parametrize(
    ["raw", "expected"],
    (
        ["PIX QRS LUPO", "PIX QRS LUPO"],
        ["PIX QRS LUPO09/01", "PIX QRS LUPO"],
        ["PIX QRS LUPO09/01   ", "PIX QRS LUPO"],
        ["PIX TRANSF  Test13/01", "PIX TRANSF  Test"],
        ["PIX TRANSF  Test    13/01", "PIX TRANSF  Test"],
    ),
)
def test_description(raw, expected):
    entry = Entry(
        dataLancamento=None,
        descricaoLancamento=raw,
        descricaoDetalhadaLancamento="",
        valorLancamento=Decimal("1.0"),
        indicadorOperacao="debito",
    )

    assert entry.description == expected
