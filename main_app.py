import streamlit as st

# App modules
from app.Assignee_Inventor_Country_Count import (
    process_country_count_data,
    show_assignee_inventor_country_count_tab,
    show_inventor_analysis_tab,
    show_entity_analysis_tab,
)
from app.Family_Priority_Count_Map import show_all_family_country_tab
from app.Timeline_Current_Owner_Count import show_timeline_current_owner_tab
from app.IPC_CPC_class import show_ipc_cpc_classification_tab
from app.Norway_Analysis import show_norway_analysis_tab


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
st.sidebar.title("Patent Dashboard Menu")

if st.sidebar.button("Refresh & Reprocess Data"):
    with st.spinner("Reprocessing all data… This may take a moment..."):
        process_country_count_data()
    st.sidebar.success("Data refreshed!")


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
        "Geographic Patent Analysis",
        "Entity Analysis",
        "Timeline Analysis",
        "Classification Analysis: IPC/CPC Codes",
        "Norway Analysis",
    ],
)


# ---------------------------------------------------------
# MAIN PAGE HEADER
# ---------------------------------------------------------
st.markdown(
    """
# Patent Landscape Dashboard

Explore patent filing trends across regions, assignees, and jurisdictions.
"""
)


# ---------------------------------------------------------
# PAGE ROUTING
# ---------------------------------------------------------
if page == "Geographic Patent Analysis":
    show_all_family_country_tab()

elif page == "Entity Analysis":
    show_entity_analysis_tab()

elif page == "Timeline Analysis":
    show_timeline_current_owner_tab()

elif page == "Classification Analysis: IPC/CPC Codes":
    show_ipc_cpc_classification_tab()

elif page == "Norway Analysis":
    show_norway_analysis_tab()
