from django.conf import settings
from google.cloud import storage
import os
import subprocess
import shutil
def get_bucket(bucket_name=settings.GS_BUCKET_NAME):
    client = storage.Client(credentials=settings.GS_CREDENTIALS)
    return client.bucket(bucket_name)

def list_files_in_bucket(bucket_name):
    bucket = get_bucket()
    blobs = bucket.list_blobs()
    return [blob.name.split('.')[0] for blob in blobs]

def delete_rar_file(rar_file_name):
    bucket = get_bucket()
    rar_file = bucket.blob(rar_file_name)
    if rar_file.exists():
        rar_file.delete()
    return rar_file

def create_rar_file(folder_path, rar_file_path):
    """
    Create a .rar file from a folder using the 'rar' command-line tool.
    """
    rar_file_full_path = os.path.join(folder_path, rar_file_path)
    try:
        subprocess.run(
            ["rar", "a", "-r", rar_file_full_path, folder_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"Created RAR file '{rar_file_path}' from folder '{folder_path}'.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating RAR file: {e.stderr.decode()}")
        raise

def upload_file_to_gcs(bucket_name, source_file_path, folder_path, destination_blob_name):
    client = storage.Client(credentials=settings.GS_CREDENTIALS)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    if blob.exists():
        blob.delete()
    blob.upload_from_filename(os.path.join(folder_path,source_file_path))
    print(f"File '{source_file_path}' uploaded to '{destination_blob_name}' in bucket '{bucket_name}'.")

def upload_folder_to_gcs(bucket_name, source_folder_path, destination_folder_name):
    client = storage.Client(credentials=settings.GS_CREDENTIALS)
    bucket = client.get_bucket(bucket_name)
    for root, _, files in os.walk(source_folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            blob = bucket.blob(f'{destination_folder_name}/{os.path.relpath(file_path, source_folder_path)}')
            blob.upload_from_filename(file_path)
            print(f"Uploaded '{file_path}' to '{blob.name}'.")

def delete_local_folder(folder_path):
    # Construct the full path to the folder in the /temp/ directory
    full_path = os.path.join(folder_path)
    
    # Check if the folder exists
    if os.path.exists(full_path) and os.path.isdir(full_path):
        # Remove the folder and all its contents
        shutil.rmtree(full_path)
        print(f"Folder '{full_path}' has been deleted.")
    else:
        print(f"Folder '{full_path}' does not exist.")

def gsutil_download_multiple(bucket_name, file_names, destination_folder):
    """
    Use gsutil to download multiple files from GCS.
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    client = storage.Client(credentials=settings.GS_CREDENTIALS)
    bucket = client.bucket(bucket_name)
    gsutil_path = 'gsutil'

    gs_images = []
    for file_name in file_names:
        if bucket.blob(file_name).exists():
            gs_images.append(f"gs://{bucket_name}/{file_name}")
        else:
            print(f"⚠️ Warning: {file_name} does not exist in GCS.")

    if not gs_images:
        print("❌ No valid files found in GCS to download.")
        return

    print(f"📥 Downloading {len(gs_images)} files...")

    for i in range(0, len(gs_images), 200):
        gsutil_command = f"{gsutil_path} -m cp {' '.join(gs_images[i:i+200])} '{destination_folder}'"
        print(f"🛠 Running command: {gsutil_command}")  # Debugging output

        try:
            result = subprocess.run(
                gsutil_command, 
                shell=True, 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            print(f"✅ Successfully downloaded {len(gs_images[i:i+200])} files.")
            print(f"🔍 GSUTIL Output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"❌ ERROR: {e.stderr}")
            raise