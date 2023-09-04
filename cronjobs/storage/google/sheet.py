import pygsheets
from loguru import logger

from cronjobs.storage.google.auth import get_auth_filepath


def insert(spreadsheet, worksheet, values):
    Spreadsheet(spreadsheet).worksheet_by_title(worksheet).insert(values)


class Spreadsheet:
    def __init__(self, spreadsheet_name, client=None):
        self.name = spreadsheet_name
        logger.info("Authenticate in Google Spreadsheet")
        self.client = client or pygsheets.authorize(service_file=get_auth_filepath())
        self.spreadsheet = self.client.open(self.name)

    def worksheet_by_title(self, title):
        return self.spreadsheet.worksheet_by_title(title)


class Worksheet:
    def __init__(self, name, spreadsheet_name=None, spreadsheet=None):
        self.name = name
        self.spreadsheet = spreadsheet or Spreadsheet(spreadsheet_name)
        self.worksheet = self.spreadsheet.worksheet_by_title(name)

    def insert(self, values, deduplicate=None):
        logger.info(f"Saving {len(values)} values to Spreadsheet")
        if deduplicate:
            values = self.deduplicate(values, deduplicate)
        self.worksheet.insert_rows(1, number=len(values), values=values)

    def get_all(self, cast=None):
        logger.info(f"Loading all rows from {self.name}")
        rows = self.worksheet.get_values(None, None)

        if cast:
            rows = [cast(r) for r in rows]

        return rows

    def deduplicate(self, values, f):
        existing_rows = self.get_all()
        return f(values, existing_rows)
