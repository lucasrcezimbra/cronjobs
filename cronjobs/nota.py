import sys
from pathlib import Path

from agilize import Agilize
from decouple import config

from cronjobs.storage.google import drive

# 1. Enviar Invoice p/ Husky
# ~2. Upload Invoice p/ Drive~
# 3. Emitir nota
# 4. Exportar nota como PDF
# 5. Exportar nota como XML
# ~6. Upload Nota PDF e XML p/ Drive~
# 7. Atualizar contabilidade
# ~8. Upload nota para Agilize~


def main(number, invoice_path, pdf_path, xml_path):
    # 2. Upload Invoice p/ Drive
    # 6. Upload Nota PDF e XML p/ Drive
    # 8. Upload nota para Agilize
    agilize = Agilize(username=config('AGILIZE_USERNAME'), password=config('AGILIZE_PASSWORD'))
    company = agilize.companies()[0]

    with open(invoice_path, 'rb') as f:
        filename, *_ = Path(f.name).name.split('.')
        drive.upload(
            file=f.read(),
            filename=f'nota{number}_{filename}.pdf',
            folder=drive.INVOICES_FOLDER,
        )

    with open(pdf_path, 'rb') as f:
        drive.upload(
            file=f.read(),
            filename=f'nota{number}.pdf',
            folder=drive.INVOICES_FOLDER,
        )

    with open(xml_path, 'rb') as f:
        data = f.read()
        drive.upload(
            file=data,
            filename=f'nota{number}_lote.xml',
            folder=drive.INVOICES_FOLDER,
        )
        company.upload_nfse(data)


if __name__ == '__main__':
    main(*sys.argv[1:])
