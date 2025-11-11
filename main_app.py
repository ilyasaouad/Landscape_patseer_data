import streamlit as st
from All_Family_Country_Map import show_all_family_country_tab

st.set_page_config(page_title="Patent Analysis Dashboard", layout="wide")

# Create tabs
(tab1,) = st.tabs(["Geographic Family Analysis"])

with tab1:
    show_all_family_country_tab()
