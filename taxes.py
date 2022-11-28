import re
import sys
from io import BytesIO

from agilize import Agilize, Competence
from decouple import config
from PyPDF2 import PdfReader

from storage.google import drive

# ~1. Subir boletos para o drive~
# 2. Pagar
# 3. Subir comprovantes para o Drive
# 4. Subir comprovantes para a Agilize
# 4. Atualizar contabilidade


def barcode_from_pdf(file):
    reader = PdfReader(BytesIO(file))
    text = reader.pages[0].extract_text()
    raw_barcode = re.search(r'[0-9 ]{48,100}', text).group()
    barcode = raw_barcode.replace(' ', '')

    if len(barcode) != 48:
        raise ValueError("Barcode doesn't have 48 numbers")

    return barcode


def main(competence):
    agilize = Agilize(username=config('AGILIZE_USERNAME'), password=config('AGILIZE_PASSWORD'))
    company = agilize.companies()[0]

    competence = Competence.from_data(competence)

    for tax in company.taxes.filter(competence):
        file = tax.download()

        if tax.abbreviation in ('DAS', 'DCTFWeb'):
            # 2. TODO: inter.pay_barcode
            print(tax.abbreviation, barcode_from_pdf(file))

        drive.upload(
            file=file,
            filename=f'{tax.abbreviation}_{competence}.pdf',
            folder=drive.TAXES_FOLDER,
        )


if __name__ == '__main__':
    main(sys.argv[1])
