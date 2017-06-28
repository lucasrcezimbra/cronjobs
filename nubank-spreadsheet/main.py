import json
import os
from datetime import date, timedelta

import pandas as pd
import pygsheets
from decouple import config
from pynubank import Nubank

def main():
    MONTHS = ['','Jan','Fev','Mar','Abr','Maio','Jun','Jul','Ago','Set','Out','Nov','Dez']
    NUBANK_CPF = config('NUBANK_CPF')
    NUBANK_PASSWORD = config('NUBANK_PASSWORD')
    SPREADSHEET = 'Gastos 2017'
    DATE = date.today() - timedelta(1)
    WORKSHEET = MONTHS[DATE.month]
    AUTH_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'service_creds.json')

    if not os.path.exists(AUTH_FILE):
        __create_auth_file(AUTH_FILE)

    print('--- Getting NuBank events ---')
    nubank = Nubank(NUBANK_CPF, NUBANK_PASSWORD)
    nubank_events = nubank.get_account_statements()

    print('--- NuBank events to DataFrame ---')
    dataframe = __create_dataframe(nubank_events)
    last_events = __get_events_records_by_date(dataframe, DATE)

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
    columns = ['time', 'title', 'description', 'nubank', 'shop', 'parcela', 'amount']
    df = pd.DataFrame(nubank_events, columns=columns)
    df['time'] = pd.to_datetime(df['time'])
    df['title'] = df['title'].apply(str.capitalize)
    df['nubank'] = 'NuBank'
    df['shop'] = df['description']
    df['parcela'] = ''
    df['amount'] = df['amount'].apply(int).apply(str).apply(lambda x: "-{},{}".format(x[0:-2],x[-2:]))
    return df

if __name__ == '__main__':
    main()
