import streamlit as st

# App modules
from app.Assignee_Inventor_Country_Count import (
    process_country_count_data,
    show_assignee_analysis_tab,
)
from app.All_Family_Country_Map import show_all_family_country_tab


# ---------------------------------------------------------
# Streamlit Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="Patent Analysis Dashboard",
    layout="wide",
    page_icon="📊",
)


# ---------------------------------------------------------
# Sidebar: Title + Refresh Button
# ---------------------------------------------------------
st.sidebar.title("🔎 Patent Dashboard Menu")

if st.sidebar.button("🔄 Refresh & Reprocess Data"):
    with st.spinner("Reprocessing all data… This may take a moment..."):
        process_country_count_data()
    st.sidebar.success("✔ Data refreshed!")


# ---------------------------------------------------------
# Preprocessing on first app load ONLY
# ---------------------------------------------------------
if "data_preprocessed" not in st.session_state:
    with st.spinner("Preparing data for the first time…"):
        process_country_count_data()
    st.session_state["data_preprocessed"] = True


# ---------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------
page = st.sidebar.radio(
    "Select View:",
    [
        "🌍 Geographic Patent Family Analysis",
        "🏢 Assignee Analysis",
    ],
)


# ---------------------------------------------------------
# MAIN PAGE HEADER
# ---------------------------------------------------------
st.markdown(
    """
# 📘 Patent Landscape Dashboard

Explore patent filing trends across regions, assignees, and jurisdictions.
"""
)


# ---------------------------------------------------------
# PAGE ROUTING
# ---------------------------------------------------------
if page == "🌍 Geographic Patent Family Analysis":
    show_all_family_country_tab()

elif page == "🏢 Assignee Analysis":
    show_assignee_analysis_tab()
