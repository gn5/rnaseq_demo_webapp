import streamlit as st
import logging

from rnaseq_viz.frontend.login import login
from rnaseq_viz.frontend.frontend import run_frontend

# Configure logger
from rnaseq_viz.config.log_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)


# Main function
def main():
    logger.info("Running frontend main()")
    if 'token' not in st.session_state:
        logger.info("No token in st.session_state")
        token = login()
        if token:
            logger.info("Setting st.session_state.token")
            st.session_state.token = token

    if 'token' in st.session_state:
        logger.info("Found st.session_state token")
        run_frontend()


if __name__ == "__main__":
    main()
