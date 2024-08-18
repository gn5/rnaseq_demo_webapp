import streamlit as st
import boto3
import logging

from rnaseq_viz.config.config import (
        COGNITO_BYPASS_AUTH, COGNITO_CLIENT_ID, COGNITO_REGION
)


# Configure logger
from rnaseq_viz.config.log_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)


# Authentication logic
def authenticate_user(username, password):
    logger.info("Running authenticate_user()")
    logger.info(f"COGNITO_BYPASS_AUTH set to {COGNITO_BYPASS_AUTH}")
    if COGNITO_BYPASS_AUTH:
        st.info("Bypassing Cognito authentication")
        return True

    logger.info("Starting Cognito authentication")
    client = boto3.client('cognito-idp', region_name=COGNITO_REGION)
    try:
        response = client.initiate_auth(
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        return response['AuthenticationResult']['AccessToken']
    except client.exceptions.NotAuthorizedException:
        st.error("Incorrect username or password")
        return False
