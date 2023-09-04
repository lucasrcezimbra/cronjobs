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
        self.spreadsheet = spreadsheet or Spreadsheet(spreadsheet_name)
        self.worksheet = self.spreadsheet.worksheet_by_title(name)

    def insert(self, values):
        logger.info("Saving {} values to Spreadsheet".format(len(values)))
        self.worksheet.insert_rows(1, number=len(values), values=values)
