import sys
from datetime import date, datetime, timedelta

import pandas as pd
from decouple import config
from pynubank import Nubank

from utils.log import logger
from spreadsheets import insert


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

    print('--- Getting NuBank events ---')
    nubank = Nubank(NUBANK_CPF, NUBANK_PASSWORD, allow_qr_code_auth=True)
    nubank_events = nubank.get_card_statements()

    print('--- NuBank events to DataFrame ---')
    dataframe = __create_dataframe(nubank_events)
    last_events = __get_events_records_by_date(dataframe, initial_datetime)

    values = [list(r) for r in last_events]
    insert(SPREADSHEET, WORKSHEET, values)


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
    df['amount'] = df['amount'].apply(int).apply(str).apply(lambda x: "-{},{}".format(x[0:-2], x[-2:]))
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
