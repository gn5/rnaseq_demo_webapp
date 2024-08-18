import logging
import pandas as pd
from pydantic import BaseModel, ValidationError, field_validator, ConfigDict
from typing import List

# Configure logger
from rnaseq_viz.config.log_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)


class RNASeqData(BaseModel):
    SYMBOL: List[str]
    samples: pd.DataFrame

    # Model configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('SYMBOL')
    def validate_symbol(cls, symbol: List[str]) -> List[str]:
        logger.info("Validating SYMBOL column...")

        # Check for NA or None values
        if any(s is None or pd.isna(s) for s in symbol):
            logger.error("Validation Error: SYMBOL column contains NA or None values.")
            raise ValueError("SYMBOL column must not contain NA or None values.")

        # Check for uniqueness
        if len(symbol) != len(set(symbol)):
            logger.error("Validation Error: SYMBOL column contains duplicate values.")
            raise ValueError("SYMBOL column must contain unique values.")

        return symbol

    @field_validator('samples', mode='before')
    def validate_samples(cls, samples: pd.DataFrame) -> pd.DataFrame:
        logger.info("Validating sample columns...")

        # Check for NA or None values
        if samples.isna().any().any():
            logger.error("Validation Error: Sample columns contain NA or None values.")
            raise ValueError("Sample columns must not contain NA or None values.")

        # Check that all sample columns are of int or float type and contain no negative values
        for col in samples.columns:
            if not samples[col].apply(lambda x: isinstance(x, (int, float)) and x >= 0).all():
                logger.error("Validation Error: All sample columns must be "
                             "of int or float type and contain no negative values.")
                raise ValueError("All sample columns must be of int or float type and contain no negative values.")

        return samples


def process_rnaseq_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the RNA-Seq DataFrame by calculating Mean, Median, and StdDev.
    Perform validation on input data.

    Args:
        df (pd.DataFrame): Input DataFrame containing RNA-Seq data with SYMBOL and sample columns.

    Returns:
        pd.DataFrame: Processed DataFrame with Mean, Median, and StdDev columns inserted before sample columns.
    """

    logger.info("Starting RNA-Seq data processing...")

    # Check that the 'SYMBOL' column exists
    if 'SYMBOL' not in df.columns:
        logger.error("SYMBOL column is missing from the DataFrame.")
        raise ValueError("SYMBOL column is required in the DataFrame.")

    # Separate the SYMBOL column from the samples
    symbol: pd.Series = df['SYMBOL']
    samples: pd.DataFrame = df.drop(columns=['SYMBOL'])

    # Validate the data using RNASeqData model
    try:
        rnaseq_data = RNASeqData(SYMBOL=symbol.tolist(), samples=samples)
    except ValidationError as e:
        logger.error(f"Data validation failed: {e}")
        raise

    # Calculate statistics
    logger.info("Calculating Mean, Median, and StdDev for each row...")
    df['Mean'] = rnaseq_data.samples.mean(axis=1)
    df['Median'] = rnaseq_data.samples.median(axis=1)
    df['StdDev'] = rnaseq_data.samples.std(axis=1)

    # Reorder the DataFrame to place SYMBOL, Mean, Median, StdDev before the sample columns
    processed_df: pd.DataFrame = df[['SYMBOL', 'Mean', 'Median', 'StdDev'] + list(rnaseq_data.samples.columns)]

    logger.info("RNA-Seq data processing completed successfully.")

    return processed_df
