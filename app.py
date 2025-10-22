import streamlit as st
import pandas as pd
from processor import melt_plate
import os
import sqlite3  # <-- For Vizualization
from pathlib import Path  # <-- For Vizualization
import plotly.express as px 

DB_FILE = Path("experiments.db")

# --- 1. Page Configuration ---
# Set the page title and a wide layout for our data
st.set_page_config(page_title="PlatePioneer", layout="wide")

# --- 2. Title and Introduction ---
st.title("🔬 PlatePioneer: 96-Well Plate Processor")
st.write("""
Upload your experiment files to process them from a 96-well grid 
into a tidy, analysis-ready CSV file.
""")

# --- 3. Sidebar for File Uploads ---
st.sidebar.header("1. Upload Your Files")

# Used st.file_uploader to create file upload widgets
# Added a callback function to clear the state if the file changes
def clear_state():
    if 'df_tidy' in st.session_state:
        del st.session_state['df_tidy']
    if 'df_results' in st.session_state:
        del st.session_state['df_results']

excel_file = st.sidebar.file_uploader(
    "Upload Excel File (.xlsx)", 
    type=["xlsx"],
    on_change=clear_state 
)
# --- 5. Main Panel for "Process" Button ---
if st.button("🚀 Process Plate Data"):
    if excel_file is not None:
        with st.spinner("Processing your data... 🪄"):
            try:
                # --- 1-5. PROCESS ALL DATA ---
                df_meta = pd.read_excel(excel_file, sheet_name="experiment_meta", header=None)
                df_results = pd.read_excel(excel_file, sheet_name="results", header=None)
                df_antibodies = pd.read_excel(excel_file, sheet_name="ta_map", header=None)
                df_concentrations = pd.read_excel(excel_file, sheet_name="concentration_map", header=None)

                meta_dict = df_meta.set_index(0)[1].to_dict()

                results_long = melt_plate(df_results, "Result_Value")
                antibodies_long = melt_plate(df_antibodies, "Antibody")
                concentrations_long = melt_plate(df_concentrations, "Concentration")

                df_tidy = results_long
                df_tidy = pd.merge(df_tidy, antibodies_long, on=['Row', 'Col'])
                df_tidy = pd.merge(df_tidy, concentrations_long, on=['Row', 'Col'])

                for key, value in meta_dict.items():
                    df_tidy[key] = value

                # --- 6. NEW: SAVE TO SESSION STATE ---
                # This is the "memory"
                st.session_state['df_tidy'] = df_tidy
                st.session_state['df_results'] = df_results # Save this for the heatmap
                st.success("✅ Processing Complete!")

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.error("Please check your Excel file has the correct 4 sheets.")
    else:
        st.warning("Please upload your Excel file first.")

# --- 7. NEW: DISPLAY RESULTS (IF THEY EXIST IN MEMORY) ---
if 'df_tidy' in st.session_state:
    st.subheader("📊 Data Visualization")

    # Create the heatmap from the *remembered* df_results
    fig = px.imshow(
        st.session_state['df_results'], # <-- Get from state
        labels=dict(x="Column", y="Row", color="Value"),
        x=[str(i) for i in range(1, 13)],
        y=[chr(ord('A') + i) for i in range(8)]
    )
    fig.update_layout(title="96-Well Plate Heatmap")

    # Use columns to show the plot and data side-by-side
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.dataframe(st.session_state['df_tidy']) # <-- Get from state

    st.subheader("💾 Save Results")

    if st.button("Save to Database", key="save_db"):
        with sqlite3.connect(DB_FILE) as con:
            # Save the *remembered* df_tidy to the database
            st.session_state['df_tidy'].to_sql(
                name="experiments",
                con=con,
                if_exists="append",
                index=False
            )
            st.success(f"Results saved to {DB_FILE}!")