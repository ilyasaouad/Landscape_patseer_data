"""
Methods 2/3 Analysis - G06F10/40 and Quantum Analysis
"""

import streamlit as st
import pandas as pd
import os
from PIL import Image

def show_methods_2_3_analysis():
    """Methods 2/3 Analysis based on G06F10/40 and Quantum keywords"""
    
    # Custom CSS for colored title
    st.markdown("""
    <style>
    .methods-title {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 20px;
    }
    .big-text {
        font-size: 1.2em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main title with different color
    st.markdown('<div class="methods-title">Methods 2/3 Analysis</div>', unsafe_allow_html=True)
    
    # Introduction paragraph
    st.markdown("""
    **About This Analysis:**
    
    This data analysis is based on more specific low-level IPC and CPC <span class="big-text">**CLASS**</span> mainly: 
    <span class="big-text">**"G06F10/40"**</span> and search word <span class="big-text">**"QUANTUM"**</span> 
    for both title, abstract and claims.
    
    The following datasets and visualizations provide detailed insights into patent landscapes 
    using these refined search criteria.
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Data directory paths
    data_dir = "data/raw-2"
    image_dir = "data/raw-2"
    
    # Define datasets and their corresponding information
    datasets = {
        "All_Family_Country": {
            "title": "📍 Patent Family Geographic Distribution",
            "description": "Analysis of patent families across different countries and jurisdictions for G06F10/40 quantum technologies."
        },
        "Assignee_Country": {
            "title": "🏢 Assignee Country Distribution", 
            "description": "Geographic distribution of patent assignees in the quantum computing domain (G06F10/40)."
        },
        "CPC_Full": {
            "title": "🏷️ Complete CPC Classification Analysis",
            "description": "Comprehensive CPC classification breakdown for quantum-related patents with G06F10/40 focus."
        },
        "IPC_Full": {
            "title": "📋 Complete IPC Classification Analysis", 
            "description": "Full IPC classification analysis for quantum technologies under G06F10/40 classification."
        },
        "Priority_Country": {
            "title": "🌍 Priority Country Analysis",
            "description": "Analysis of priority countries for quantum patent applications in G06F10/40 domain."
        },
        "Timeline_Current_Owner": {
            "title": "📈 Timeline Analysis by Current Owner",
            "description": "Temporal trends of quantum patent filings by current patent owners in G06F10/40 classification."
        }
    }
    
    # Process each dataset
    for dataset_name, info in datasets.items():
        st.markdown(f"### {info['title']}")
        st.markdown(f"*{info['description']}*")
        
        # Try to load CSV data
        csv_file = f"{data_dir}/{dataset_name}.csv"
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                st.markdown("**Dataset Overview:**")
                st.dataframe(df.head(10), use_container_width=True)
                st.markdown(f"**Total Records:** {len(df)}")
            except Exception as e:
                st.warning(f"Could not load CSV data: {e}")
                st.info("CSV data file exists but could not be processed. Please check the file format.")
        else:
            st.info(f"CSV data file not found at: {csv_file}")
            st.markdown("*This dataset is available for analysis when the corresponding CSV file is provided.*")
        
        # Load and display corresponding image
        image_file = f"{image_dir}/{dataset_name}.jpeg"
        if os.path.exists(image_file):
            try:
                image = Image.open(image_file)
                st.image(image, caption=f"Visualization: {info['title']}", use_container_width=True)
            except Exception as e:
                st.error(f"Could not load image: {e}")
        else:
            st.warning(f"Image not found: {image_file}")
        
        st.markdown("---")
    
    # Summary section
    st.markdown("### 📊 Analysis Summary")
    st.markdown("""
    This Methods 2/3 Analysis focuses specifically on:
    
    - **Classification Focus:** G06F10/40 (Quantum computing hardware and architectures)
    - **Keyword Search:** "QUANTUM" in title, abstract, and claims
    """)