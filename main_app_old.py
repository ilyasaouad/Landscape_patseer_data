import streamlit as st
from Assignee_Inventor_Country_from_patseer_data import process_data
from app.Family_Priority_Count_Map import show_all_family_country_tab
from Assignee_Count import show_assignee_count_tab
from Assignee_Inventor_Country_Count import process_country_count_data

st.set_page_config(page_title="Patent Analysis Dashboard", layout="wide")

# Execute data processing first
process_country_count_data()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Analysis:", ["Geographic Family Analysis", "Assignee Analysis"]
)

# Display selected page
if page == "Geographic Family Analysis":
    show_all_family_country_tab()
elif page == "Assignee Analysis":
    show_assignee_count_tab()
