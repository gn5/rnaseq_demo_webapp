import logging
import streamlit as st

from rnaseq_viz.frontend.auth import authenticate_user


# Configure logger
from rnaseq_viz.config.log_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)


# Streamlit UI for login
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        token = authenticate_user(username, password)
        if token:
            st.success("Login successful")
            return token
        else:
            st.error("Login failed")
