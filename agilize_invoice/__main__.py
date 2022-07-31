import sys
from pathlib import Path

from agilize import Agilize, Competence
from decouple import config


def main(competence):
    agilize = Agilize(username=config('AGILIZE_USERNAME'), password=config('AGILIZE_PASSWORD'))
    company = agilize.companies()[0]

    competence = Competence.from_data(competence)
    invoice = company.invoices.get(competence)

    filepath = Path.home() / 'Downloads' / f'agilize{competence}_nota.jpg'

    with open(filepath, 'wb') as f:
        f.write(invoice.download_nfse())


if __name__ == '__main__':
    main(sys.argv[1])
