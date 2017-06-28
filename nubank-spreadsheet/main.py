import os
from datetime import date, timedelta

import pandas as pd
import pygsheets
from decouple import config
from pynubank import Nubank

def main():
    NUBANK_CPF = config('NUBANK_CPF')
    NUBANK_PASSWORD = config('NUBANK_PASSWORD')
    SPREADSHEET = 'Gastos 2017'
    WORKSHEET = 'NuBank'
    AUTH_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'service_creds.json')

    print('--- Getting NuBank events ---')
    nubank = Nubank(NUBANK_CPF, NUBANK_PASSWORD)
    nubank_events = nubank.get_account_statements()

    print('--- NuBank events to DataFrame ---')
    dataframe = __create_dataframe(nubank_events)
    last_events = __get_yesterday_events_records(dataframe)

    print('--- Authenticate in Google Spreadsheet ---')
    gc = pygsheets.authorize(service_file=AUTH_FILE)

    print('--- Saving {} values to Spreadsheet ---'.format(len(last_events)))
    worksheet = gc.open(SPREADSHEET).worksheet_by_title(WORKSHEET)
    values = [list(r) for r in last_events]
    worksheet.insert_rows(1, number=len(values), values=values)

def __get_yesterday_events_records(dataframe):
    yesterday = date.today() - timedelta(1)
    last_events = dataframe.loc[dataframe['time'] > yesterday]
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
