import sys
from datetime import date, datetime, timedelta
from getpass import getpass

import pandas
from decouple import config
from pyitau import Itau

from cronjobs.logs import get_logger
from cronjobs.storage.google import sheet

logger = get_logger(__name__)


def main(initial_date=None):
    if not initial_date:
        initial_date = date.today() - timedelta(1)

    MONTHS = [
        '',
        'Jan', 'Fev', 'Mar', 'Abr', 'Maio', 'Jun',
        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
    ]
    SPREADSHEET = 'Gastos {}'.format(initial_date.year)
    WORKSHEET = MONTHS[initial_date.month]

    logger.info('Getting Itaú events')
    itau = Itau(
        agency=config('ITAU_AGENCY'),
        account=config('ITAU_ACCOUNT'),
        account_digit=config('ITAU_ACCOUNT_DIGIT'),
        password=getpass('Senha do Itaú: '),
        holder=config('ITAU_HOLDER'),
    )
    itau.authenticate()
    events = itau.get_statements()['lancamentos']

    logger.info('Itaú events to DataFrame')
    dataframe = __create_dataframe(events, initial_date)
    last_events = list(dataframe.to_records(index=False))

    values = [list(r) for r in last_events]
    sheet.insert(SPREADSHEET, WORKSHEET, values)


def __create_dataframe(events, date):
    df = __create_account_dataframe(events)

    df['date'] = df['date'].apply(lambda x: x.date())
    df = df.loc[df['date'] >= date]
    df.sort_values('date', inplace=True)
    df['date'] = df['date'].apply(str)

    df = df.loc[df['description'] != 'SDO CTA/APL AUTOMATICAS']

    df.reset_index(inplace=True, drop=True)

    df['category'] = df.index + 2
    df['category'] = df['category'].apply(
        lambda i: '=VLOOKUP(F{};Categorias!F:G;2;FALSE)'.format(i))

    df['location2'] = df.index + 2
    df['location2'] = df['location2'].apply(
        lambda i: '=VLOOKUP(E{};Categorias!E:F;2;FALSE)'.format(i))

    df['total'] = df.index + 2
    df['total'] = df['total'].apply(lambda i: '=H{}+I{}'.format(i, i))

    return df


def __create_account_dataframe(events):
    columns = [
        'dataLancamento', 'category', 'nr', 'descricaoLancamento', 'itau',
        'location', 'location2', 'parcela', 'valorLancamento', 'reembolso',
        'total', 'ePositivo',
    ]
    columns_mapper = {
        'dataLancamento': 'date',
        'descricaoLancamento': 'description',
        'valorLancamento': 'amount'
    }
    df = pandas.DataFrame(events, columns=columns)
    df.rename(columns=columns_mapper, inplace=True)
    df['date'] = pandas.to_datetime(df['date'], format='%d/%m/%Y')
    df['category'] = None
    df['nr'] = None
    df['itau'] = 'Itaú'
    df['location'] = df['description']
    df['location2'] = None
    df['parcela'] = None
    df['amount'] = df['amount'].apply(lambda x: x.replace('.', '') if x else 0)
    df['amount'] = df['amount'].apply(lambda x: x.replace(',', '.') if x else 0)
    df['amount'] = df['amount'].apply(float)
    df.loc[df['ePositivo'] == False, 'amount'] = df['amount'].apply(lambda x: x * -1)  # noqa
    df['reembolso'] = None
    df['total'] = None
    del df['ePositivo']
    return df


if __name__ == '__main__':
    if len(sys.argv) > 1:
        initial_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
        main(initial_date)
    else:
        main()