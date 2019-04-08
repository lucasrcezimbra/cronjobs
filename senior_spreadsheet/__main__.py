from decouple import config
from senior_hcm import SeniorHcm

from spreadsheets import insert


SPREADSHEET = 'Contabilidade Pessoal'
WORKSHEET = 'Diário Senior HCM'


def main():
    print('--- Getting Senior HCM events ---')
    senior = SeniorHcm(config('SENIOR_EMAIL'), config('SENIOR_PASSWORD'))
    payroll = senior.get_last_payroll()

    print('--- Payroll to Accounting ---')
    date = payroll['calculation']['paymentDate']

    types = payroll['wageTypes']
    result = []

    for type_ in types:
        if type_['wageType']['type'] == 'PROCEEDS':
            proceed = [date, type_['actualValue'], 'AR', 'BCI', type_['wageType']['name']]
            result.append(proceed)
        elif type_['wageType']['type'] == 'DEDUCTION':
            deduction = [date, type_['actualValue'], 'BCI', '', type_['wageType']['name']]
            result.append(deduction)

    insert(SPREADSHEET, WORKSHEET, result)


if __name__ == '__main__':
    main()
