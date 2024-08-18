import boto3
import logging
import pandas as pd
from io import BytesIO
from botocore.client import BaseClient
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


from rnaseq_viz.config.config import USE_LOCALSTACK


# Configure logger
from rnaseq_viz.config.log_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)


class S3Manager:
    def __init__(self):
        logger.info("Initializing S3Manager...")
        if USE_LOCALSTACK:
            logger.info("Using localstack S3 client")
            self._s3_client = boto3.client(
                "s3",
                endpoint_url="http://localhost:4566",
                aws_access_key_id="test",
                aws_secret_access_key="test",
                region_name="us-east-1"
            )
        else:
            logger.info("Not using localstack")
            boto3.setup_default_session()
            self._s3_client = boto3.client("s3")

    @property
    def s3_client(self) -> BaseClient:
        logger.debug("Getting S3 client...")
        return self._s3_client

    def upload_file_to_s3(self, file_obj: BytesIO, bucket: str, s3_file_name: str) -> str:
        logger.info(f"Uploading file to S3 bucket {bucket} with S3 key {s3_file_name}...")
        try:
            self.s3_client.upload_fileobj(file_obj, bucket, s3_file_name)
            logger.info(f"Upload Successful: s3://{bucket}/{s3_file_name}")
            return s3_file_name
        except (NoCredentialsError, PartialCredentialsError) as e:
            logger.error(f"Credentials error: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred during file upload: {e}")
            raise

    def read_csv_from_s3(self, bucket: str, key: str) -> pd.DataFrame:
        logger.info(f"Reading CSV file from S3 bucket {bucket} with key {key}...")
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            df = pd.read_csv(BytesIO(response['Body'].read()))
            logger.info("CSV file read successfully")
            return df
        except Exception as e:
            logger.error(f"An error occurred while reading the CSV file: {e}")
            raise

    def download_file_from_s3(self, bucket: str, key: str, filename: str) -> bool:
        logger.info(f"Downloading file from S3 bucket {bucket} with key {key} to local file {filename}...")
        try:
            self.s3_client.download_file(bucket, key, filename)
            logger.info(f"Downloaded file from S3: {filename}")
            return True
        except Exception as e:
            logger.error(f"An error occurred while downloading the file: {e}")
            raise
