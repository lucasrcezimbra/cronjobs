import sys

from agilize import Agilize, Competence
from decouple import config

from cronjobs.storage.google import drive


def main(competence):
    agilize = Agilize(
        username=config("AGILIZE_USERNAME"), password=config("AGILIZE_PASSWORD")
    )
    company = agilize.companies()[0]

    competence = Competence.from_data(competence)
    prolabore = company.prolabores.get(competence)

    drive.upload(
        file=prolabore.download(),
        filename=f"{competence}-Lucas Rangel Cezimbra.pdf",
        folder=drive.PROLABORE_FOLDER,
    )


if __name__ == "__main__":
    main(sys.argv[1])
