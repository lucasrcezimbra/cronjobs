import sys

from agilize import Agilize, Competence
from decouple import config
from inter import Inter

from logs import get_logger
from storage.google import drive

# ~1. Subir nota pro Google Drive~
# ~2. Pagar boleto~
# 3. Atualizar contabilidade
# 4. Subir comprovante pro Google Drive


logger = get_logger(__name__)


def main(competence):
    agilize = Agilize(username=config('AGILIZE_USERNAME'), password=config('AGILIZE_PASSWORD'))
    inter = Inter(
        client_id=config('INTER_CLIENT_ID'),
        client_secret=config('INTER_CLIENT_SECRET'),
        cert_path=config('INTER_CERT_PATH'),
        key_path=config('INTER_KEY_PATH'),
    )

    logger.info('Loading Agilize Company')
    company = agilize.companies()[0]

    logger.info('Loading Invoice')
    competence = Competence.from_data(competence)
    invoice = company.invoices.get(competence)

    logger.info('Upating NFSe to Drive')
    drive.upload(
        file=invoice.download_nfse(),
        filename=f'agilize{competence}_nota.jpg',
        folder=drive.PAYMENTS_FOLDER,
    )

    logger.info('Paying barcode')
    result = inter.pay_barcode(invoice.barcode, invoice.amount, invoice.due_date)
    logger.info(result)


if __name__ == '__main__':
    main(sys.argv[1])
    logger.info('Done')
