import sys

from agilize import Agilize, Competence
from decouple import config
from loguru import logger

from cronjobs.storage.google import drive


def main(competence):
    logger.info("Starting...")
    agilize = Agilize(
        username=config("AGILIZE_USERNAME"), password=config("AGILIZE_PASSWORD")
    )
    logger.info("Loading Agilize Company")
    company = agilize.companies()[0]

    logger.info("Loading Prolabore")
    competence = Competence.from_data(competence)
    prolabore = company.prolabores.get(competence)

    logger.info("Uploading Prolabore PDF")
    drive.upload(
        file=prolabore.download(),
        filename=f"{competence}-Lucas Rangel Cezimbra.pdf",
        folder=drive.PROLABORE_FOLDER,
    )
    logger.success("Finish")


if __name__ == "__main__":
    main(sys.argv[1])
