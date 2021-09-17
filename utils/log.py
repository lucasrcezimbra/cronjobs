import logging
from logging import StreamHandler
from logging.handlers import SMTPHandler

from decouple import Csv, config


def get_logger():
    logger = logging.getLogger()

    if not logger.handlers:
        email_host = config('EMAIL_LOGGER_HOST')
        email_port = config('EMAIL_LOGGER_PORT')
        email_from = config('EMAIL_LOGGER_FROM')
        email_to = config('EMAIL_LOGGER_TO', cast=Csv())
        email_subject = config('EMAIL_LOGGER_SUBJECT')
        email_username = config('EMAIL_LOGGER_HOST_USER')
        email_password = config('EMAIL_LOGGER_HOST_PASSWORD')

        email_host_port = (email_host, email_port)
        email_credentials = (email_username, email_password)

        smtp_handler = SMTPHandler(email_host_port, email_from, email_to,
                                   email_subject, credentials=email_credentials)

        logger.addHandler(StreamHandler())
        logger.addHandler(smtp_handler)

    return logger


logger = get_logger()
