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
from app.Methods_2_3_Analysis import show_methods_2_3_analysis


# ---------------------------------------------------------
# Streamlit Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="Patent Analysis Dashboard",
    layout="wide",
    page_icon="📊",
)


# ---------------------------------------------------------
# Initialize data processing flag (but skip actual processing)
# ---------------------------------------------------------
# Set the flag so modules know data is "available" without processing
if "data_preprocessed" not in st.session_state:
    st.session_state["data_preprocessed"] = True  # Skip processing, assume data exists


# ---------------------------------------------------------
# Navigation
# ---------------------------------------------------------
st.sidebar.markdown("## 📊 Analysis Menu")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select Analysis:",
    [
        "📍 Geographic Patent Analysis",
        "👥 Entity Analysis", 
        "📈 Timeline Analysis",
        "🏷️ Classification Analysis: IPC/CPC Codes",
        "🇳🇴 Norway Analysis",
        "🔬 Methods 2/3 Analysis",
    ],
    format_func=lambda x: x.split(" ", 1)[1] if " " in x else x
)

# Add special styling for Methods 2/3 Analysis
st.sidebar.markdown("""
<style>
div[data-testid="stRadio"] > label:last-child > div {
    background-color: #ff6b35 !important;
    color: white !important;
    font-weight: bold !important;
    font-size: 1.2em !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    margin: 20px 0 4px 0 !important;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# MAIN PAGE HEADER
# ---------------------------------------------------------
st.markdown(
    """
# Patent Landscape Analysis

Explore patent filing trends across regions, assignees, and jurisdictions.

**About This Analysis:** This patent landscape analysis is designed to provide insights and examples of analytical approaches specifically for Class G06N10 (quantum computing technologies). This is just a draft before final analysis.
"""
)


# ---------------------------------------------------------
# PAGE ROUTING
# ---------------------------------------------------------
if "Geographic Patent Analysis" in page:
    show_all_family_country_tab()

elif "Entity Analysis" in page:
    show_entity_analysis_tab()

elif "Timeline Analysis" in page:
    show_timeline_current_owner_tab()

elif "Classification Analysis: IPC/CPC Codes" in page:
    show_ipc_cpc_classification_tab()

elif "Methods 2/3 Analysis" in page:
    show_methods_2_3_analysis()

elif "Norway Analysis" in page:
    show_norway_analysis_tab()