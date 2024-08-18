from fastapi import FastAPI, BackgroundTasks, Body
import logging
import uvicorn

from rnaseq_viz.common.s3_manager import S3Manager
from rnaseq_viz.config.config import (
    BACKEND_HOST, BACKEND_PORT, BACKEND_N_WORKERS, LOG_LEVEL
)
from rnaseq_viz.backend.task_manager import TaskManager

from rnaseq_viz.config.log_config import setup_logging, LOG_FORMAT

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize S3Manager and TaskManager
s3_manager = S3Manager()
task_manager = TaskManager(s3_manager)


@app.post("/start-processing/")
def start_processing(
    s3_key: str = Body(..., embed=True),
    folder: str = Body(..., embed=True),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    logger.info(f"Received processing request for S3 key {s3_key} in folder {folder}...")
    task_id = task_manager.start_task(s3_key, folder, background_tasks)
    return {"task_id": task_id}


@app.get("/check-status/{task_id}")
def check_status(task_id: str):
    logger.info(f"Checking status for task ID {task_id}...")
    return task_manager.get_task_status(task_id)


def run_backend():
    logger.info("Starting FastAPI server...")
    logger.info(f"Spawning {BACKEND_N_WORKERS} uvicorn workers at log level {LOG_LEVEL}")
    uvicorn.run(
        "rnaseq_viz.backend.main:app",
        host=BACKEND_HOST,
        port=BACKEND_PORT,
        workers=BACKEND_N_WORKERS,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": LOG_FORMAT,
                },
            },
            "handlers": {
                "default": {
                    "level": logging.getLevelName(LOG_LEVEL),
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                },
            },
            "loggers": {
                "": {
                    "handlers": ["default"],
                    "level": logging.getLevelName(LOG_LEVEL),
                },
                "uvicorn.error": {
                    "level": logging.getLevelName(LOG_LEVEL),
                },
                "uvicorn.access": {
                    "level": logging.getLevelName(LOG_LEVEL),
                    "propagate": False,
                },
            },
        },
    )


if __name__ == "__main__":
    run_backend()
