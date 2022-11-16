import sys

from agilize import Agilize, Competence
from decouple import config

from storage.google import drive


def main(competence):
    agilize = Agilize(username=config('AGILIZE_USERNAME'), password=config('AGILIZE_PASSWORD'))
    company = agilize.companies()[0]

    competence = Competence.from_data(competence)
    invoice = company.invoices.get(competence)

    drive.upload(
        file=invoice.download_nfse(),
        filename=f'agilize{competence}_nota.jpg',
        folder=drive.PAYMENTS_FOLDER,
    )


if __name__ == '__main__':
    main(sys.argv[1])
