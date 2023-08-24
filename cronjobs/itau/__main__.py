import sys
from datetime import date

from decouple import config
from pyitau import Itau

from cronjobs.itau import checking_account, credit_card, sheet


def main(date_):
    itau = Itau(
        agency=config('ITAU_AGENCY'),
        account=config('ITAU_ACCOUNT'),
        account_digit=config('ITAU_ACCOUNT_DIGIT'),
        password=config('ITAU_PASSWORD'),
        holder_name=config('ITAU_HOLDER_NAME', default=None),
    )
    itau.authenticate()
    rows_credit_card = credit_card.data_to_rows(itau.get_credit_card_invoice(), date_.month)
    rows_checking_account = checking_account.data_to_rows(
        itau.get_statements_from_month(year=2023, month=date_.month), date_
    )
    sheet.insert(rows_credit_card, date_)
    sheet.insert(rows_checking_account, date_)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python -m cronjobs.itau <year>-<month>-<day>')

    main(date.fromisoformat(sys.argv[1]))
