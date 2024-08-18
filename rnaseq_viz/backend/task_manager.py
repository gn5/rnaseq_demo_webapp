from typing import Dict
import logging
import pandas as pd
from fastapi import HTTPException

from rnaseq_viz.common.s3_manager import S3Manager
from rnaseq_viz.backend.data_processing import process_rnaseq_data
from rnaseq_viz.config.config import S3_BUCKET
from rnaseq_viz.common.utils import generate_unique_temp_path

# Configure logger
from rnaseq_viz.config.log_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(self, s3_manager: S3Manager):
        self.s3_manager = s3_manager
        self.tasks: Dict[str, Dict] = {}

    def start_task(self, s3_key: str, folder: str, background_tasks) -> str:
        task_id = f"task_{len(self.tasks) + 1}"
        self.tasks[task_id] = {"status": "processing"}
        background_tasks.add_task(self.process_file, task_id, s3_key, folder)
        logger.info(f"Processing started with task ID {task_id}")
        return task_id

    def get_task_status(self, task_id: str) -> Dict:
        task = self.tasks.get(task_id)
        if not task:
            logger.error(f"Task ID {task_id} not found")
            raise HTTPException(status_code=404, detail="Invalid task ID")
        logger.info(f"Task {task_id} status: {task['status']}")
        return task

    def process_file(self, task_id: str, s3_key: str, folder: str):
        logger.info(f"Starting processing for task {task_id} with S3 key {s3_key} in folder {folder}...")
        try:
            # Generate a unique path for the local temporary file
            local_file = generate_unique_temp_path(prefix="/tmp", filename=f"{task_id}.csv")
            self.s3_manager.download_file_from_s3(bucket=S3_BUCKET, key=s3_key, filename=local_file)

            df = pd.read_csv(local_file)

            # Process the DataFrame and validate the data
            processed_df = process_rnaseq_data(df)

            processed_s3_key = f"{folder}/processed/{task_id}_processed.csv"
            processed_file = generate_unique_temp_path(prefix="/tmp", filename=f"{task_id}_processed.csv")
            processed_df.to_csv(processed_file, index=False)
            result_s3_key = self.s3_manager.upload_file_to_s3(file_obj=open(processed_file, "rb"),
                                                              bucket=S3_BUCKET,
                                                              s3_file_name=processed_s3_key)

            self.tasks[task_id]['status'] = 'completed'
            self.tasks[task_id]['result'] = result_s3_key
            logger.info(f"Task {task_id} completed successfully. Result stored at {result_s3_key}")
        except Exception as e:
            self.tasks[task_id]['status'] = 'failed'
            self.tasks[task_id]['result'] = str(e)
            logger.error(f"Task {task_id} failed: {e}")
