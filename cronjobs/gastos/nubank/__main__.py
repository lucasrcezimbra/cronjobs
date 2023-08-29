import sys
from datetime import date

from decouple import config
from pynubank import Nubank

from cronjobs.gastos import sheet
from cronjobs.gastos.nubank import credit_card
from cronjobs.logs import get_logger

logger = get_logger(__name__)


def main(date_):
    year_month = date_.strftime("%Y-%m")

    nubank = Nubank()
    logger.info("Authenticating with Nubank")
    nubank.authenticate_with_cert(
        cpf=config("NUBANK_CPF"),
        password=config("NUBANK_PASSWORD"),
        cert_path=config("NUBANK_CERT_PATH"),
    )

    logger.info("Requesting bills")
    bills_data = nubank.get_bills()
    logger.info("Requesting card statements")
    card_statements_data = nubank.get_card_statements()

    bill_data = credit_card.get_bill_data(bills_data, year_month)
    bill_detail_data = nubank.get_bill_details(bill_data)

    rows_credit_card = credit_card.data_to_rows(
        bill_detail_data=bill_detail_data,
        card_statements_data=card_statements_data,
        nubank=nubank,
        year_month=year_month,
    )

    logger.info(f"Inserting {len(rows_credit_card)} rows into the spreadsheet")
    sheet.insert(rows_credit_card, date_)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m cronjobs.gastos.nubank <year>-<month>-<day>")

    main(date.fromisoformat(sys.argv[1]))
