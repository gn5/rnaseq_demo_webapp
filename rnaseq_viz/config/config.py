import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Logging level
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

# S3 Configuration
S3_BUCKET = os.getenv('S3_BUCKET', 'scratch')

# Backend Configuration
BACKEND_HOST = os.getenv('BACKEND_HOST', '0.0.0.0')
BACKEND_PORT = int(os.getenv('BACKEND_PORT', '8001'))
BACKEND_N_WORKERS = int(os.getenv('BACKEND_N_WORKERS', '1'))

# Frontend Configuration
# URL for frontend to access backend
BACKEND_ACCESS_URL = os.getenv('BACKEND_ACCCESS_URL', f'http://localhost:{BACKEND_PORT}')

# Configuration for retry mechanism
# Number of retries
FRONTEND_RETRY_COUNT = int(os.getenv('FRONTEND_RETRY_COUNT', 5))
# Delay between retries in seconds
FRONTEND_RETRY_DELAY_SECONDS = int(os.getenv('FRONTEND_RETRY_DELAY_SECONDS', 2))


# LocalStack Configuration
USE_LOCALSTACK = os.getenv('USE_LOCALSTACK', 'false').lower() == 'true'

# Cognito Configuration
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
COGNITO_CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
COGNITO_REGION = os.getenv('COGNITO_REGION', 'us-east-1')
COGNITO_BYPASS_AUTH = os.getenv('COGNITO_BYPASS_AUTH', 'false').lower() == 'true'
