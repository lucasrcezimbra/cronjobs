import pygsheets
from loguru import logger

from cronjobs.storage.google.auth import get_auth_filepath


def insert(spreadsheet, worksheet, values):
    logger.info("Authenticate in Google Spreadsheet")
    gc = pygsheets.authorize(service_file=get_auth_filepath())

    logger.info("Saving {} values to Spreadsheet".format(len(values)))
    worksheet = gc.open(spreadsheet).worksheet_by_title(worksheet)
    worksheet.insert_rows(1, number=len(values), values=values)
