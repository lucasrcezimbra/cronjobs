import sys
from getpass import getpass

from decouple import config
from pyitau import Itau

from cronjobs.itau import credit_card, sheet


def main(month):
    itau = Itau(
        agency=config('ITAU_AGENCY'),
        account=config('ITAU_ACCOUNT'),
        account_digit=config('ITAU_ACCOUNT_DIGIT'),
        password=config('ITAU_PASSWORD', default=lambda: getpass('Senha do Itaú: ')),
        holder=config('ITAU_HOLDER', default=None),
    )
    itau.authenticate()
    rows = credit_card.data_to_rows(itau.get_credit_card_invoice(), month)
    sheet.insert(rows, month)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python -m cronjobs.itau <month: int>')

    main(int(sys.argv[1]))
