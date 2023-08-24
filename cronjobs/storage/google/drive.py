import mimetypes
from io import BytesIO

from decouple import config
from google.auth import load_credentials_from_file
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from cronjobs.storage.google.auth import get_auth_filepath

INVOICES_FOLDER = 'INVOICES_FOLDER'
PAYMENTS_FOLDER = 'PAYMENTS_FOLDER '
PROLABORE_FOLDER = 'PROLABORE_FOLDER'
TAXES_FOLDER = 'TAXES_FOLDER'

PARENTS = {
    INVOICES_FOLDER: config('INVOICES_FOLDER_ID'),
    PAYMENTS_FOLDER: config('PAYMENTS_FOLDER_ID'),
    PROLABORE_FOLDER: config('PROLABORE_FOLDER_ID'),
    TAXES_FOLDER: config('TAXES_FOLDER_ID'),
}


def upload(file, filename, folder):
    creds, _ = load_credentials_from_file(get_auth_filepath())
    service = build('drive', 'v3', credentials=creds)
    metadata = {'name': filename, 'parents': [PARENTS[folder]]}
    file = MediaIoBaseUpload(BytesIO(file), mimetype=mimetypes.guess_type(filename)[0])
    service.files().create(body=metadata, media_body=file).execute()
