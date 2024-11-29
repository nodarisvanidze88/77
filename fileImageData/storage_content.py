from django.conf import settings
from google.cloud import storage

def list_files_in_bucket(bucket_name):
    client = storage.Client(credentials=settings.GS_CREDENTIALS)
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    return [blob.name.split('.')[0] for blob in blobs]
