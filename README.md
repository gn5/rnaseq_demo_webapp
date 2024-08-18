# RNA-Seq Analysis Application

## Overview

The RNA-Seq Analysis Application is a web-based tool designed to facilitate the analysis of RNA-Seq data. Users can upload RNA-Seq data in CSV format, which is then processed by custom algorithms on the backend, and the results are displayed interactively on the frontend. The application utilizes a Streamlit-based frontend and a FastAPI backend, with S3 used for data storage. During development, LocalStack is employed to mock S3 services, and Cognito is bypassed locally for ease of testing and development.

The results displayed currently are:
- a table of mean expression, median and standard deviation per gene
- a distribution of mean expression

## Dependencies

- **Operating System**: Tested on Linux
- **Python**: Version `3.10.11`
- **Poetry**: Version `1.6.1`
- **Docker**: Required for running LocalStack and other services

## How to Run

1. **Set Up Environment Variables**: Configure your environment variables in the [.env](.env) file, as well as the variables specified at the top of [Makefile](Makefile), particularly the paths to Python, Poetry, and Streamlit.

2. **Set Up Mocked S3 with LocalStack**:
    ```bash
    make setup-s3
    ```

3. **Run the Backend**:
    ```bash
    make run-backend
    ```

4. **Run the Frontend**:
    ```bash
    make run-frontend
    ```

5. **Access the Application**:
    Open your web browser and navigate to `http://localhost:8501` to access the frontend.

5. **Provide input CSV**:
    After login (leave user and password blank if Cognito auth is bypassed in `.env`), Provide an input CSV of RNAseq data. See example file at [test_data/test_input_data.csv](test_data/test_input_data.csv). The gene ID column must be called `SYMBOL`, and all the other columns will automatically be assumed to be samples. Values are taken to be raw gene expression counts, which must be equal or higher than 0 (integers, not float).

## Available Makefile Commands

- `make install`: Install the necessary Python dependencies.
- `make setup-s3`: Start LocalStack and create the S3 bucket.
- `make run-backend`: Run the FastAPI backend server.
- `make run-frontend`: Run the Streamlit frontend application.
- `make clean`: Clean the virtual environment.
- `make rebuild`: Rebuild the virtual environment from scratch.
- `make start-localstack`: Start LocalStack services.
- `make kill-localstack`: Stop any running LocalStack containers.
- `make build-docker-backend`: Build backend docker image that can be deployed in production.
- `make build-docker-frontend`: Build frontend docker image that can be deployed in production.

## Deployment in Production

- The 2 docker images can be pushed to AWS ECR and deployed in AWS EKS (Kubernetes) where they can easily scale to accomodate a large volume of end-user requests.
- AWS Cognito can be used for the frontend authentication.
- An S3 bucket needs to deployed as well, to be used as data storage for frontend uploads and backend data processing.

## Screenshots

![Alt text](/screenshots/1_login.png?raw=true "Login")
![Alt text](/screenshots/2_login_success.png?raw=true "Login Success")
![Alt text](/screenshots/3_file_upload.png?raw=true "File Upload")
![Alt text](/screenshots/4_processing_complete.png?raw=true "Processing Complete")
![Alt text](/screenshots/5_plot.png?raw=true "Plots")


## Possible Improvements
- Better separate the frontend and backend configurations, required environment variables, and dependencies (e.g., create separate pyproject.toml files for each).
- Add unit tests, especially for the backend processing logic.
- Implement persistent user sessions.
- Replace the REST protocol for frontend-to-backend communication with WebSocket for near-instant polling of backend results.
- Use LocalStack Pro (which is not free) to fully test integration with AWS Cognito and AWS EKS locally.
- add CI/CD for automating cloud dev or prod deployment.
- Add new visualizations based on user feedback, such as a volcano plot for gene visualization, and a slider to highlight genes under a certain p-value threshold.
