import re
import sys
from io import BytesIO

from agilize import Agilize, Competence
from decouple import config
from inter import Inter
from loguru import logger
from PyPDF2 import PdfReader

from cronjobs.storage.google import drive

# ~1. Subir boletos para o drive~
# ~2. Pagar~
# 3. Subir comprovantes para o Drive
# 4. Subir comprovantes para a Agilize
# 4. Atualizar contabilidade


def barcode_from_pdf(file):
    reader = PdfReader(BytesIO(file))
    text = reader.pages[0].extract_text()
    raw_barcode = re.search(r"[0-9 ]{48,100}", text).group()
    barcode = raw_barcode.replace(" ", "")

    if len(barcode) != 48:
        raise ValueError("Barcode doesn't have 48 numbers")

    return barcode


def main(competence):
    agilize = Agilize(
        username=config("AGILIZE_USERNAME"), password=config("AGILIZE_PASSWORD")
    )
    inter = Inter(
        client_id=config("INTER_CLIENT_ID"),
        client_secret=config("INTER_CLIENT_SECRET"),
        cert_path=config("INTER_CERT_PATH"),
        key_path=config("INTER_KEY_PATH"),
    )

    logger.info("Loading Agilize Company")
    company = agilize.companies()[0]
    competence = Competence.from_data(competence)

    for tax in company.taxes.filter(competence):
        if tax.amount == 0:
            logger.info(f"Skipping {tax.abbreviation}")
            continue

        logger.info(f"Downloading {tax.abbreviation}")
        file = tax.download()

        logger.info(f"Uploading {tax.abbreviation}")
        drive.upload(
            file=file,
            filename=f"{tax.abbreviation}_{competence}.pdf",
            folder=drive.TAXES_FOLDER,
        )

        if tax.abbreviation in ("DAS", "DCTFWeb"):
            barcode = barcode_from_pdf(file)
            logger.info(f"Paying {tax.abbreviation}: {barcode}")
            inter.pay_barcode(barcode, tax.amount, tax.due_date)


if __name__ == "__main__":
    main(sys.argv[1])
    logger.info("Done")
