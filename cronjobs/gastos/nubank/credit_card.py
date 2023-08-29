from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from attrs import define
from cattrs import Converter
from loguru import logger

from cronjobs.gastos.sheet import Row

converter = Converter()
converter.register_structure_hook(Decimal, lambda v, _: Decimal(str(v / 100)))
converter.register_structure_hook(
    date, lambda v, _: datetime.strptime(v, "%Y-%m-%d").date()
)


def get_bill_data(bills_data, year_month):
    return next(
        b for b in bills_data if b["summary"]["due_date"].startswith(year_month)
    )


def data_to_rows(bill_detail_data, card_statements_data, nubank, year_month):
    bill = converter.structure(bill_detail_data["bill"], Bill)
    return bill.to_rows(card_statements_data, nubank, year_month)


@define
class Entry:
    amount: Decimal
    title: str
    post_date: date
    charges: int = 1
    transaction_id: Optional[str] = None

    def find_statement(self, statements_data):
        logger.info(f"Finding statement for transaction {self.transaction_id}")
        return next(s for s in statements_data if s["id"] == self.transaction_id)

    def get_details(self, statements_data, nubank):
        statement = self.find_statement(statements_data)
        logger.info(f'Requesting card details for statement {statement["id"]}')
        return nubank.get_card_statement_details(statement)

    def get_installments(self, statements_data, nubank, year_month):
        details = self.get_details(statements_data, nubank)
        charges = details["transaction"]["charges_list"]
        return [c for c in charges if c["post_date"].startswith(year_month)]

    def get_installment_index(self, statements_data, nubank, year_month):
        if not self.transaction_id:
            return "x"

        installments = self.get_installments(statements_data, nubank, year_month)

        if not installments:
            return "x"

        return installments[0]["index"]

    def get_installment(self, statements_data, nubank, year_month):
        if self.charges == 1:
            return

        installment_index = self.get_installment_index(
            statements_data, nubank, year_month
        )
        return f"{installment_index}/{self.charges}"

    def to_row(self, statements_data, nubank, year_month):
        return Row(
            date_=str(self.post_date),
            description=self.title,
            bank="Nubank Lucas",
            business_raw=self.title,
            installment=self.get_installment(statements_data, nubank, year_month),
            value=str(-self.amount).replace(".", ","),
        )


@define
class Bill:
    line_items: List[Entry]

    def to_rows(self, card_statements_data, nubank, year_month):
        return [
            e.to_row(card_statements_data, nubank, year_month) for e in self.line_items
        ]
