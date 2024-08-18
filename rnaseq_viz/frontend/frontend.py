import requests
import logging
import time

import streamlit as st

from rnaseq_viz.frontend.viz_utils import display_results
from rnaseq_viz.common.s3_manager import S3Manager
from rnaseq_viz.common.utils import generate_unique_s3_folder
from rnaseq_viz.config.config import (
    BACKEND_ACCESS_URL,
    S3_BUCKET,
    FRONTEND_RETRY_COUNT,
    FRONTEND_RETRY_DELAY_SECONDS
)

from rnaseq_viz.config.log_config import setup_logging

# Configure logger
setup_logging()
logger = logging.getLogger(__name__)

# Initialize S3Manager
s3_manager = S3Manager()


def upload_file_to_s3(uploaded_file):
    """Uploads the file to S3 and returns the unique S3 key and folder."""
    try:
        unique_s3_folder = generate_unique_s3_folder()
        s3_key = f"{unique_s3_folder}/uploads/{uploaded_file.name}"
        s3_manager.upload_file_to_s3(file_obj=uploaded_file, bucket=S3_BUCKET, s3_file_name=s3_key)
        logger.info(f"File uploaded successfully: {s3_key}")
        st.success("File uploaded successfully!")
        return s3_key, unique_s3_folder
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logger.error(f"An error occurred during upload: {str(e)}")
        return None, None


def start_processing_task(s3_key, folder):
    """Starts the processing task by sending a request to the FastAPI backend."""
    logger.info(f"Starting processing task with s3_key: {s3_key} and folder: {folder}")
    payload = {
        "s3_key": s3_key,
        "folder": folder
    }
    response = requests.post(f"{BACKEND_ACCESS_URL}/start-processing", json=payload)
    if response.status_code == 200:
        task_id = response.json()["task_id"]
        st.write(f"Processing started with task ID: {task_id}")
        return task_id
    else:
        st.error("Failed to start processing.")
        logger.error(f"Failed to start processing. Status code: {response.status_code}, Response: {response.text}")
        return None


def check_task_status(task_id):
    """Checks the status of the processing task with retry logic for specific errors."""
    retries = 0
    while True:
        response = requests.get(f"{BACKEND_ACCESS_URL}/check-status/{task_id}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404 and "Invalid task ID" in response.text:
            retries += 1
            if retries >= FRONTEND_RETRY_COUNT:
                st.error("Failed to check processing status after multiple attempts.")
                logger.error("Failed to check processing status after multiple attempts.")
                return None
            logger.info(f"Retrying to check task status... Attempt {retries}/{FRONTEND_RETRY_COUNT}")
            time.sleep(FRONTEND_RETRY_DELAY_SECONDS)
        else:
            st.error(f"Failed to check processing status. Status code: {response.status_code}")
            logger.error(f"Failed to check processing status. Status code: {response.status_code}, "
                         f"Response: {response.text}")
            return None


def download_and_display_results(result_key):
    """Downloads the processed file from S3 and displays the results."""
    df = s3_manager.read_csv_from_s3(bucket=S3_BUCKET, key=result_key)
    if df is not None:
        logger.info("Processed DataFrame is not None. Displaying results.")
        logger.info(f"{df.head(2)}")
        display_results(df)
    else:
        st.error("Failed to download the processed file from S3.")
        logger.error("Failed to download the processed file from S3.")


def run_frontend():
    """Main function to run the Streamlit frontend."""
    logger.info("Running run_frontend()")
    st.title("RNA-Seq Analysis")

    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file is not None:
        s3_key, folder = upload_file_to_s3(uploaded_file)
        if s3_key and folder and st.button("Start Processing"):
            task_id = start_processing_task(s3_key, folder)
            if task_id:
                while True:
                    status = check_task_status(task_id)
                    if status:
                        if status['status'] == 'completed':
                            st.success("Processing completed!")
                            st.write("Downloading processed file...")
                            download_and_display_results(status['result'])
                            break
                        elif status['status'] == 'failed':
                            st.error(f"Processing failed: {status['result']}")
                            logger.error(f"Processing failed: {status['result']}")
                            break
                        else:
                            st.write("Processing...")
                            time.sleep(2)  # Poll every 2 seconds
                    else:
                        break
