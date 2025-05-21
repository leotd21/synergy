import streamlit as st
import pandas as pd

def upload_file():
    return st.file_uploader("Upload your CSV file", type=["csv"], key="uploaded_file")

def display_dataframe(label, df):
    st.subheader(label)
    st.dataframe(df.head())

def select_num_rows(default):
    return st.number_input(
        "Number of synthetic rows",
        min_value=10,
        max_value=10000,
        value=default,
        key="num_rows"
    )

def select_model():
    return st.selectbox(
        "Choose a synthesizer",
        ["GaussianCopula", "CTGAN", "TVAE"],
        key="model_type"
    )

def generate_button():
    return st.button("Generate Synthetic Data", key="generate_btn")

def download_button(df):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Download Synthetic Data",
        csv,
        "synthetic_data.csv",
        "text/csv",
        key="download_button"
    )
