from datetime import date
from decimal import Decimal

from cronjobs.gastos.itau.credit_card import Entry


def test_business_and_installment():
    assert Entry._business_and_installment("COMPRA CREDITO") == ("COMPRA CREDITO", "")
    assert Entry._business_and_installment("COMPRA CREDITO         ") == (
        "COMPRA CREDITO",
        "",
    )
    assert Entry._business_and_installment("COMPRA CREDITO (1/2)") == (
        "COMPRA CREDITO",
        "1/2",
    )
    assert Entry._business_and_installment("COMPRA CREDITO (01/02)") == (
        "COMPRA CREDITO",
        "01/02",
    )
    assert Entry._business_and_installment("COMPRA CREDITO (01/02)") == (
        "COMPRA CREDITO",
        "01/02",
    )
    assert Entry._business_and_installment("COMPRA CREDITO 1/2") == (
        "COMPRA CREDITO",
        "1/2",
    )
    assert Entry._business_and_installment("COMPRA CREDITO  (01/02)  ") == (
        "COMPRA CREDITO",
        "01/02",
    )


def test_installment():
    entry = Entry(
        data=date.today(),
        descricao="COMPRA CREDITO",
        valor=Decimal("1.0"),
        sinalValor="-",
    )

    assert entry.installment == ""

    entry.descricao = "COMPRA CREDITO (1/2)"
    assert entry.installment == "1/2"

    entry.descricao = "COMPRA CREDITO (01/02)"
    assert entry.installment == "01/02"

    entry.descricao = "COMPRA CREDITO 1/2"
    assert entry.installment == "1/2"

    entry.descricao = "COMPRA CREDITO  (01/02)  "
    assert entry.installment == "01/02"

    entry.descricao = "COMPRA CREDITO  (01/02)  "
    assert entry.installment == "01/02"

    entry.descricao = "COMPRA CREDITO  (01/02)  "
    assert entry.installment == "01/02"


def test_business():
    entry = Entry(
        data=date.today(),
        descricao="COMPRA CREDITO",
        valor=Decimal("1.0"),
        sinalValor="-",
    )

    assert entry.business == "COMPRA CREDITO"

    entry.descricao = "COMPRA CREDITO (1/2)"
    assert entry.business == "COMPRA CREDITO"

    entry.descricao = "COMPRA CREDITO (01/02)"
    assert entry.business == "COMPRA CREDITO"

    entry.descricao = "COMPRA CREDITO 1/2"
    assert entry.business == "COMPRA CREDITO"

    entry.descricao = "COMPRA CREDITO  (01/02)  "
    assert entry.business == "COMPRA CREDITO"

    entry.descricao = "COMPRA CREDITO  (01/02)  "
    assert entry.business == "COMPRA CREDITO"

    entry.descricao = "COMPRA CREDITO  (01/02)  "
    assert entry.business == "COMPRA CREDITO"
