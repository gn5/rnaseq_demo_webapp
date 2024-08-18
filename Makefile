# Variables
# python, poetry and streamlit must be installed locally:
PYTHON = $(VENV_PATH)/bin/python
POETRY = /usr/bin/pyenv/versions/3.10.11/bin/poetry
STREAMLIT = $(VENV_PATH)/bin/streamlit
VENV_PATH = .venv

# Docker variables
BACKEND_IMAGE_NAME=backend-image
FRONTEND_IMAGE_NAME=frontend-image


# Set up the poetry virtual environment
$(VENV_PATH)/bin/activate: pyproject.toml
	$(POETRY) install || $(POETRY) install --no-root
	touch $(VENV_PATH)/bin/activate


# Kill any existing LocalStack containers
.PHONY: kill-localstack
kill-localstack:
	@echo "Killing any existing LocalStack containers..."
	@docker ps -a -q --filter "ancestor=localstack/localstack" | xargs -r docker rm -f


# Start LocalStack
.PHONY: start-localstack
start-localstack: kill-localstack
	@echo "Starting LocalStack..."
	@export $(shell sed 's/^/export /' .env | grep '=' | grep -v '#') && \
	set -x && \
	docker run --rm -d -p $${LOCALSTACK_PORT}:$${LOCALSTACK_PORT} -e SERVICES=s3 localstack/localstack


# Create the S3 bucket in LocalStack
.PHONY: setup-s3
setup-s3: start-localstack
	@echo "Creating S3 bucket in LocalStack..."
	@export $(shell sed 's/^/export /' .env | grep '=' | grep -v '#') && \
	set -x && \
	AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test \
	aws --endpoint-url=http://$${LOCALSTACK_HOST}:$${LOCALSTACK_PORT} \
		    s3 mb s3://$${S3_BUCKET}


# List all objects in the S3 bucket recursively
.PHONY: list-s3
list-s3:
	@echo "Listing all objects in S3 bucket recursively..."
	@export $(shell sed 's/^/export /' .env | grep '=' | grep -v '#') && \
	set -x && \
	AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test \
		aws s3 ls s3://$${S3_BUCKET} \
		--recursive --endpoint-url=http://$${LOCALSTACK_HOST}:$${LOCALSTACK_PORT}


# Run the backend server locally
.PHONY: run-backend
run-backend: $(VENV_PATH)/bin/activate
	$(PYTHON) rnaseq_viz/backend/main.py


# Run the frontend application locally
.PHONY: run-frontend
run-frontend: $(VENV_PATH)/bin/activate
	$(STREAMLIT) run rnaseq_viz/frontend/main.py


# Build 2 docker images, backend and frontend, for deployment in AWS EKS
build-docker-backend:
	docker build -t $(BACKEND_IMAGE_NAME):0.0.1 -f docker/Dockerfile.backend .

build-docker-frontend:
	docker build -t $(FRONTEND_IMAGE_NAME):0.0.1 -f docker/Dockerfile.frontend .
