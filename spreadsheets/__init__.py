import json
import os

import pygsheets
from decouple import config


def __create_auth_file(filepath):
    auth_dict = {
        'type': config('AUTH_TYPE'),
        'project_id': config('AUTH_PROJECT_ID'),
        'private_key_id': config('AUTH_PRIVATE_KEY_ID'),
        'private_key': config('AUTH_PRIVATE_KEY', cast=lambda v: v.replace('\\n', '\n')),
        'client_email': config('AUTH_CLIENT_EMAIL'),
        'client_id': config('AUTH_CLIENT_ID'),
        'auth_uri': config('AUTH_AUTH_URI'),
        'token_uri': config('AUTH_TOKEN_URI'),
        'auth_provider_x509_cert_url': config('AUTH_AUTH_PROVIDER_X509_CERT_URL'),
        'client_x509_cert_url': config('AUTH_CLIENT_X509_CERT_URL'),
    }
    with open(filepath, 'w') as fp:
        json.dump(auth_dict, fp)


def insert(spreadsheet, worksheet, values):
    AUTH_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'service_creds.json')

    if not os.path.exists(AUTH_FILE):
        __create_auth_file(AUTH_FILE)

    print('--- Authenticate in Google Spreadsheet ---')
    gc = pygsheets.authorize(service_file=AUTH_FILE)

    print('--- Saving {} values to Spreadsheet ---'.format(len(values)))
    worksheet = gc.open(spreadsheet).worksheet_by_title(worksheet)
    worksheet.insert_rows(1, number=len(values), values=values)
