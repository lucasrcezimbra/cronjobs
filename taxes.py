import sys

from agilize import Agilize, Competence
from decouple import config

from storage.google import drive


def main(competence):
    agilize = Agilize(username=config('AGILIZE_USERNAME'), password=config('AGILIZE_PASSWORD'))
    company = agilize.companies()[0]

    competence = Competence.from_data(competence)

    for tax in company.taxes.filter(competence):
        drive.upload(
            file=tax.download(),
            filename=f'{tax.abbreviation}_{competence}.pdf',
            folder=drive.TAXES_FOLDER,
        )


if __name__ == '__main__':
    main(sys.argv[1])
