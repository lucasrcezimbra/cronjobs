from io import BytesIO

from decouple import config
from google.auth import load_credentials_from_file
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from storage.google.auth import get_auth_filepath

PROLABORE_FOLDER = 'PROLABORE_FOLDER'

PARENTS = {
    PROLABORE_FOLDER: config('PROLABORE_FOLDER_ID'),
}

MIMETYPES = {
    'pdf': 'application/pdf',
}


def mimetype(filename):
    extension = filename.split('.')[-1]
    return MIMETYPES[extension]


def upload(file, filename, folder):
    creds, _ = load_credentials_from_file(get_auth_filepath())
    service = build('drive', 'v3', credentials=creds)
    metadata = {'name': filename, 'parents': [PARENTS[folder]]}
    file = MediaIoBaseUpload(BytesIO(file), mimetype=mimetype(filename))
    service.files().create(body=metadata, media_body=file).execute()