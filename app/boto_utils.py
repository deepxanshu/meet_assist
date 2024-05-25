import asyncio
import datetime
import io
import logging
import pathlib
import random
import string
import pandas as pd
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from botocore.exceptions import ClientError
from starlette.datastructures import UploadFile

from app.boto_client_setup import S3_CLIENT, SHORT_URL_TABLE

DOCUMENT_EXPIRE_TTL = 60 * 60 * 2


@contextmanager
def temp_file(filename):
    """
    generate a temporary file with the exact name as specified

    returns the filepath of the generated file (path like object)

    usage:
    ---
    with temp_file(filename) as fpath:
        <code using fpath>
    """

    with TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)

        filepath = tmpdir / filename
        filepath.touch()

        yield filepath


async def _upload_file(file, filename, bucket_name: str, object_name: str):
    """
    upload file to s3
    :param file: file to be uploaded
    :param bucket_name: name of the bucket to put the file in
    :param object_name: object name that will be saved in s3
    :return: True if successfully uploaded
    """

    with temp_file(filename) as tmp_file:
        with open(tmp_file, "wb") as f:
            f.write(file.read())

        try:
            S3_CLIENT.upload_file(str(tmp_file), bucket_name, object_name)

        except ClientError as e:
            logging.error(e)
            return False

    return True

async def upload_files_to_s3(file, filename, bucket: str, s3_path: str = ""):
    if not s3_path.endswith('/'):
        s3_path += '/'  # Ensure there's a trailing slash

    object_name = f"{s3_path}{filename}" if s3_path else filename

    # Note: No need to wrap _upload_file in a list if only uploading one file
    result = await _upload_file(file, filename, bucket, object_name)

    if not result:
        raise Exception("Upload failed.")

    return result
def fetch_and_process_user_data(phone_number, bucket_name, s3_directory_base="webroot/meet-assist"):
    s3_directory = f"{s3_directory_base}/{phone_number}"
    user_data = []

    # List objects in the user's folder
    response = S3_CLIENT.list_objects_v2(Bucket=bucket_name, Prefix=s3_directory)
    
    if 'Contents' in response:
        for obj in response['Contents']:
            # Make sure the object size is within your limit (5MB in this case)
            if obj['Size'] <= 5 * 1024 * 1024:
                file_key = obj['Key']
                # Get the object from S3
                obj_response = S3_CLIENT.get_object(Bucket=bucket_name, Key=file_key)
                
                # Assuming these are CSV files. Adjust according to your data format.
                df = pd.read_csv(obj_response['Body'])
                # Append or process the data as needed
                user_data.append(df)

    # Now, `user_data` contains the data frames of the user's meeting data from S3 files
    # You can then process this data further or store it in `all_meeting_data` for the seek functionality

    # Assuming you're processing or analyzing data here
    processed_data = process_user_data(user_data)
    
    # Store or use this processed data as needed for your application
    return processed_data

def process_user_data(user_data):
    # Placeholder for your data processing/analysis logic
    # For example, concatenating all DataFrames into one, filtering, etc.
    combined_df = pd.concat(user_data, ignore_index=True)
    # Perform any analysis or data extraction as needed
    # Return processed data or insights
    return combined_df

async def download_file_from_s3(file_identifier, file_path, bucket):
    """
    downloads file from s3 and returns in memory byte object
    :param file_identifier: key to identify the file
    :param file_path: s3 file path in the format `s3/load_file?filePath=S3_DIRECTORY_PATH`
    :param bucket: bucket name in which file is present
    :returns: byte object of the file
    """

    file_obj = io.BytesIO()

    S3_CLIENT.download_fileobj(bucket, file_path[file_path.index("=") + 1 :], file_obj)
    file_obj.seek(0)
    logging.info("image downloaded successfully.")

    return file_identifier, file_obj


async def download_files_from_s3(file_dict, bucket):
    """
    download multiple files from s3 and returns in memory byte object
    :param file_dict: with key as file identifier
        and value as s3 file path in the format `s3/load_file?filePath=S3_DIRECTORY_PATH`
    :param bucket: s3 bucket name
    :returns: byte object of the file
    """

    tasks = [
        download_file_from_s3(name, path, bucket) for name, path in file_dict.items()
    ]

    return dict(await asyncio.gather(*tasks))


def get_item_from_shorturl_table(short_url_hash):
    return SHORT_URL_TABLE.get_item(Key={"hash": short_url_hash}).get("Item")


def make_short_url(long_url, customer_id, template_id):
    def generate_random(n):
        """
        generate random string of length n
        :param n: int depicting size of random string
        :return: random string of length n
        """

        return "".join(
            random.SystemRandom().choice(string.ascii_lowercase + string.digits)
            for _ in range(n)
        )

    customer_id = str(customer_id)
    short_id = generate_random(10)

    current_epoch_time = int(datetime.datetime.now().timestamp())
    SHORT_URL_TABLE.put_item(
        TableName="url_redirect",
        Item={
            "hash": short_id,
            "meta_data": {"customer_id": customer_id, "template_id": template_id},
            "website_redirect_location": long_url,
            "creation_time": current_epoch_time,
            "ttl": current_epoch_time + 60 * 60 * 24 * 7,
        },
    )
    public_short_url = "https://u.st-f.in/" + short_id

    return public_short_url


def generate_presigned_url(path, bucket="stashfin-storage-dev", ttl=DOCUMENT_EXPIRE_TTL):
    url = S3_CLIENT.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket, "Key": path},
        ExpiresIn=ttl,
    )

    return url


async def upload_file_object_to_s3(path, bucket, body):
    file = io.BytesIO(body)
    S3_CLIENT.upload_fileobj(file, bucket, path)
 
    return path

async def upload_file(filename, bucket_name, s3_key):

    with open(filename, "rb") as file:
        S3_CLIENT.upload_fileobj(file, bucket_name, s3_key)