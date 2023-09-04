import pytest

from cronjobs.gastos.sheet import Row, deduplicate


@pytest.fixture
def row(faker):
    return Row(
        date_=faker.date_object(),
        categoria=faker.word(),
        recurrent=faker.word(),
        description=faker.word(),
        bank=faker.word(),
        business_raw=faker.word(),
        business=faker.word(),
        installment=faker.word(),
        value=faker.word(),
    )


def test_row_eq(row):
    row2 = Row(
        date_=row.date_,
        categoria=row.categoria,
        recurrent=row.recurrent,
        description=row.description,
        bank=row.bank,
        business_raw=row.business_raw,
        business=row.business,
        installment=row.installment,
        value=row.value,
        new=row.new,
    )

    assert row == row2


def test_row_eq_ignore_some_fields(row):
    row2 = Row(
        date_=row.date_,
        categoria="ignored",
        recurrent=row.recurrent,
        description="ignored",
        bank=row.bank,
        business_raw=row.business_raw,
        business="ignored",
        installment=row.installment,
        value=row.value,
        new="ignored",
    )

    assert row == row2


def test_deduplicate(row):
    rows = [row]
    existing_rows = [row]

    assert deduplicate(rows, existing_rows) == []


def test_deduplicate_ignore_some_fields(row):
    rows = [row]
    existing_rows = [
        Row(
            date_=row.date_,
            categoria="ignored",
            recurrent=row.recurrent,
            description="ignored",
            bank=row.bank,
            business_raw=row.business_raw,
            business="ignored",
            installment=row.installment,
            value=row.value,
            new="ignored",
        )
    ]

    assert deduplicate(rows, existing_rows) == []
    assert deduplicate(existing_rows, rows) == []
