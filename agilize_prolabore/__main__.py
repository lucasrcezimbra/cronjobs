import sys
from pathlib import Path

from agilize import Agilize, Competence
from decouple import config


def main(competence):
    agilize = Agilize(username=config('AGILIZE_USERNAME'), password=config('AGILIZE_PASSWORD'))
    company = agilize.companies()[0]

    competence = Competence.from_data(competence)
    prolabore = company.prolabores.get(competence)

    filepath = Path.home() / 'Downloads' / f'{competence}-Lucas Rangel Cezimbra.pdf'

    with open(filepath, 'wb') as f:
        f.write(prolabore.download())


if __name__ == '__main__':
    main(sys.argv[1])
