import requests
from django.conf import settings
import csv
from io import TextIOWrapper, BytesIO

def get_CSV_File_content():
  dataPath = settings.GOOGLE_SHEET
  response = requests.get(dataPath)
  response.raise_for_status()
  csvContent = response.text
  decoded_content = csvContent.encode('iso-8859-1').decode('utf-8')
  csv_bytes_like = BytesIO(decoded_content.encode('utf-8'))
  return csv.DictReader(TextIOWrapper(csv_bytes_like, encoding='utf-8-sig'))