import os
import time
import uuid


def generate_unique_s3_folder() -> str:
    """
    Generate a unique S3 folder name using a timestamp and a randomly generated UUID.

    Returns:
        str: The unique S3 folder name.
    """
    # Get the current timestamp
    timestamp = int(time.time())

    # Generate a random UUID
    unique_id = uuid.uuid4()

    # Combine to create a unique folder name
    return f"{timestamp}-{unique_id}"


def generate_unique_temp_path(prefix: str = "/tmp", filename: str = "") -> str:
    """
    Generate a unique temporary file path using a timestamp and a randomly generated UUID.

    Args:
        prefix (str): The directory where the temporary file will be stored.
        filename (str): The original filename to be included in the path.

    Returns:
        str: The unique temporary file path.
    """
    # Get the current timestamp
    timestamp = int(time.time())

    # Generate a random UUID
    unique_id = uuid.uuid4()

    # Combine to create a unique path
    unique_filename = f"{filename}-{timestamp}-{unique_id}"

    # Return the complete temporary file path
    return os.path.join(prefix, unique_filename)
