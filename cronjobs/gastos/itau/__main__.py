import sys
from datetime import date

from decouple import config
from loguru import logger
from pyitau import Itau

from cronjobs.gastos import sheet
from cronjobs.gastos.itau import checking_account, credit_card


def main(date_):
    logger.info(f"Running Itaú {date_}")
    itau = Itau(
        agency=config("ITAU_AGENCY"),
        account=config("ITAU_ACCOUNT"),
        account_digit=config("ITAU_ACCOUNT_DIGIT"),
        password=config("ITAU_PASSWORD"),
        holder_name=config("ITAU_HOLDER_NAME", default=None),
    )

    logger.info("Requesting authentication")
    itau.authenticate()

    logger.info("Requesting Credit Card Invoice")
    credit_card_data = itau.get_credit_card_invoice()
    rows_credit_card = credit_card.data_to_rows(credit_card_data, date_.month)

    logger.info("Requesting Checking Account Statements")
    checking_account_data = itau.get_statements_from_month(
        year=date_.year, month=date_.month
    )
    rows_checking_account = list(
        checking_account.data_to_rows(checking_account_data, date_)
    )

    logger.info(f"Inserting {len(rows_credit_card)} credit card rows")
    sheet.insert(rows_credit_card, date_)
    logger.info(f"Inserting {len(rows_checking_account)} checking account rows")
    sheet.insert(rows_checking_account, date_)
    logger.success("Done Itaú")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m cronjobs.gastos.itau <year>-<month>-<day>")

    main(date.fromisoformat(sys.argv[1]))
