import json
import os
import sys
from datetime import date, datetime, timedelta

import pandas as pd
import pygsheets
from decouple import config
from pynubank import Nubank

from utils.log import logger


def main(initial_date=None):
    if not initial_date:
        initial_date = date.today() - timedelta(1)
    initial_datetime = datetime.combine(initial_date, datetime.min.time())
    initial_datetime = initial_datetime.astimezone()

    MONTHS = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Maio', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    NUBANK_CPF = config('NUBANK_CPF')
    NUBANK_PASSWORD = config('NUBANK_PASSWORD')
    SPREADSHEET = 'Gastos {}'.format(date.today().year)
    WORKSHEET = MONTHS[initial_datetime.month]
    AUTH_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'service_creds.json')

    if not os.path.exists(AUTH_FILE):
        __create_auth_file(AUTH_FILE)

    print('--- Getting NuBank events ---')
    nubank = Nubank(NUBANK_CPF, NUBANK_PASSWORD)
    nubank_events = nubank.get_card_statements()

    print('--- NuBank events to DataFrame ---')
    dataframe = __create_dataframe(nubank_events)
    last_events = __get_events_records_by_date(dataframe, initial_datetime)

    print('--- Authenticate in Google Spreadsheet ---')
    gc = pygsheets.authorize(service_file=AUTH_FILE)

    print('--- Saving {} values to Spreadsheet ---'.format(len(last_events)))
    worksheet = gc.open(SPREADSHEET).worksheet_by_title(WORKSHEET)
    values = [list(r) for r in last_events]
    worksheet.insert_rows(1, number=len(values), values=values)


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


def __get_events_records_by_date(dataframe, date):
    last_events = dataframe.loc[dataframe['time'] > date]
    last_events['time'] = last_events['time'].apply(str)
    return list(last_events.to_records(index=False))


def __create_dataframe(nubank_events):
    columns = ['time', 'category', 'description', 'nubank', 'shop', 'shop2', 'parcela', 'amount', 'reembolso', 'total']
    df = pd.DataFrame(nubank_events, columns=columns)
    df['time'] = pd.to_datetime(df['time'])
    df['category'] = df.index + 2
    df['category'] = df['category'].apply(lambda i: '=VLOOKUP(F{};Categorias!H:I;2;FALSE)'.format(i))
    df['nubank'] = 'NuBank'
    df['shop'] = df['description']
    df['shop2'] = df.index + 2
    df['shop2'] = df['shop2'].apply(lambda i: '=VLOOKUP(E{};Categorias!E:F;2;FALSE)'.format(i))
    df['description'] = None
    df['parcela'] = ''
    df['amount'] = df['amount'].apply(int).apply(str).apply(lambda x: "-{},{}".format(x[0:-2],x[-2:]))
    df['reembolso'] = None
    df['total'] = df.index + 2
    df['total'] = df['total'].apply(lambda i: '=H{}+I{}'.format(i, i))
    return df


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            initial_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
            main(initial_date)
        else:
            main()
    except Exception as e:
        logger.exception(e)
