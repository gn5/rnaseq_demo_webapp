import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def display_results(df):
    """
    Display the processed data in a table and plot the distribution of mean expression.

    Args:
        df (pandas.DataFrame): The processed DataFrame containing RNA-Seq analysis results.
    """
    # Display the processed data in a table
    st.dataframe(df)

    # Determine cutoff for the right tail
    cutoff = np.percentile(df['Mean'], 95)

    # Plot distribution of mean expression with cutoff
    st.write("Distribution of Mean Expression (Cutoff applied)")
    plt.figure(figsize=(10, 6))
    sns.histplot(df[df['Mean'] <= cutoff]['Mean'], kde=True, bins=30)  # Apply cutoff
    plt.title("Distribution of Mean Expression")
    plt.xlabel("Mean Expression")
    plt.ylabel("Frequency")
    st.pyplot(plt)  # Streamlit function to display the plot
