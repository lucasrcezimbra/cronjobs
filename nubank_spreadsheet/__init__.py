from datetime import date, timedelta

import pandas as pd
from decouple import config
from pynubank import Nubank

from logs import get_logger
from spreadsheets import insert

logger = get_logger(__name__)


def main(initial_date=None):
    if not initial_date:
        initial_date = date.today() - timedelta(1)

    MONTHS = [
        '',
        'Jan', 'Fev', 'Mar', 'Abr', 'Maio', 'Jun',
        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
    ]
    NUBANK_CPF = config('NUBANK_CPF')
    NUBANK_PASSWORD = config('NUBANK_PASSWORD')
    SPREADSHEET = 'Gastos {}'.format(initial_date.year)
    WORKSHEET = MONTHS[initial_date.month]

    logger.info('Authenticating')
    nubank = Nubank()
    nubank.authenticate_with_cert(NUBANK_CPF, NUBANK_PASSWORD, 'cert.p12')

    logger.info('Getting NuBank events')
    credit_events = nubank.get_card_statements()
    debit_events = nubank.get_account_statements()

    logger.info('NuBank events to DataFrame')
    dataframe = __create_dataframe(credit_events, debit_events, initial_date)
    last_events = list(dataframe.to_records(index=False))

    values = [list(r) for r in last_events]
    insert(SPREADSHEET, WORKSHEET, values)


def __create_dataframe(credit_events, debit_events, date):
    credit_dataframe = __create_credit_dataframe(credit_events)
    debit_dataframe = __create_debit_dataframe(debit_events)

    df = pd.concat((credit_dataframe, debit_dataframe))

    df['time'] = df['time'].apply(lambda x: x.date())
    df = df.loc[df['time'] >= date]
    df.sort_values('time', inplace=True)
    df['time'] = df['time'].apply(str)

    df.reset_index(inplace=True, drop=True)

    df['category'] = df.index + 2
    df['category'] = df['category'].apply(
        lambda i: '=VLOOKUP(F{};Categorias!F:G;2;FALSE)'.format(i))

    df['shop2'] = df.index + 2
    df['shop2'] = df['shop2'].apply(
        lambda i: '=VLOOKUP(E{};Categorias!E:F;2;FALSE)'.format(i))

    df['total'] = df.index + 2
    df['total'] = df['total'].apply(lambda i: '=H{}+I{}'.format(i, i))

    return df


def __create_credit_dataframe(events):
    columns = [
        'time', 'category', 'description', 'nubank', 'shop', 'shop2',
        'parcela', 'amount', 'reembolso', 'total',
    ]
    df = pd.DataFrame(events, columns=columns)
    df['time'] = pd.to_datetime(df['time'])
    df['nubank'] = 'NuBank'
    df['shop'] = df['description']
    df['description'] = None
    df['parcela'] = ''
    df['amount'] = df['amount'].apply(int).apply(lambda x: (x / 100) * -1)
    df['reembolso'] = None
    return df


def __create_debit_dataframe(events):
    columns = [
        '__typename', 'postDate', 'category', 'title', 'nubank', 'shop',
        'shop2', 'destinationAccount', 'originAccount', 'detail', 'parcela', 'amount',
        'reembolso', 'total'
    ]
    df = pd.DataFrame(events, columns=columns)
    df.rename(columns={'title': 'description', 'postDate': 'time'},
              inplace=True)
    df['time'] = pd.to_datetime(df['time'])
    df['category'] = None
    df['nubank'] = 'NuConta'
    df['destinationAccount'] = df['destinationAccount'].apply(pd.Series)['name']
    df['originAccount'] = df['originAccount'].apply(pd.Series)['name']
    df.fillna('', inplace=True)

    df['shop'] = df["destinationAccount"] + df["originAccount"]
    df.loc[df['shop'] == '', 'shop'] = df['detail']

    df['parcela'] = None
    df.loc[df['__typename'] == 'BarcodePaymentEvent', 'amount'] = (
        df['amount'].apply(lambda x: x * -1)
    )
    df.loc[df['__typename'] == 'DebitPurchaseEvent', 'amount'] = (
        df['amount'].apply(lambda x: x * -1)
    )
    df.loc[df['__typename'] == 'TransferOutEvent', 'amount'] = (
        df['amount'].apply(lambda x: x * -1)
    )
    df.loc[df['__typename'] == 'PixTransferOutEvent', 'amount'] = (
        df['amount'].apply(lambda x: x * -1)
    )
    del df['destinationAccount']
    del df['originAccount']
    del df['detail']
    del df['__typename']
    return df
