#!/usr/bin/env python3
"""
Patent Landscape Analysis - Display Application
Complete replica of main_app.py functionality using processed CSV files
Designed for Streamlit Cloud deployment
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import os

# Page configuration
st.set_page_config(
    page_title="Patent Landscape Analysis",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_csv_data(file_path):
    """Load CSV data with caching"""
    try:
        if os.path.exists(file_path):
            return pd.read_csv(file_path, encoding='utf-8')
        return None
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return None

# Load all processed data
@st.cache_data
def load_all_data():
    """Load all processed CSV files"""
    data = {}
    
    # All data sources
    files = {
        'family_country': 'data/raw/All_family_Country_Map.csv',
        'priority_country': 'data/raw/Priority_Country_Map.csv',
        'assignee_data': 'data/processed/Assignee_Country_Count_Updated.csv',
        'inventor_data': 'data/processed/Inventor_Country_Count.csv',
        'ipc_data': 'data/processed/Top_IPC_Assignee_Count.csv',
        'cpc_data': 'data/processed/Top_CPC_Assignee_Count.csv',
        'cpc_temporal': 'data/processed/CPC_Classifications_vs_Year.csv',
        'timeline_owner': 'data/raw/Innovation_Timeline_(Current_Owner_-_Application_Date).csv'
    }
    
    for key, file_path in files.items():
        loaded_data = load_csv_data(file_path)
        if loaded_data is not None:
            data[key] = loaded_data
    
    return data

def show_geographic_analysis(data):
    """Geographic Patent Analysis with Family and Priority tabs"""
    
    st.title("Geographic Patent Analysis")
    
    # Explanatory comment
    st.markdown("""
    **Understanding Priority vs Family Countries:**  
    The priority country table shows where each invention was first filed. The patent family table shows where the same inventions were later filed internationally. The priority filing itself is not counted again in the family table.
    
    That is why some countries have many priority filings but fewer family filings - most applications start in the priority country, but they are not filed again in that same country when the applicant expands internationally.
    
    **Example:** Finland (FI) has many priority filings because many inventions originate there, but FI appears less often in the family table since an invention that starts in FI is usually filed later in EP, US, or WO, and not again in FI. As a result, FI ranks high in the Priority Countries tab but low in the family table (see Priority Countries tab).
    """)
    
    # Create tabs
    tab1, tab2 = st.tabs(["📍 Patent Families", "🌍 Priority Countries"])
    
    with tab1:
        st.subheader("Patent Families Analysis")
        
        if 'family_country' in data and not data['family_country'].empty:
            df_family = data['family_country'].dropna()
            
            # Get total column
            total_cols = [col for col in df_family.columns if 'total' in col.lower()]
            if total_cols:
                total_col = total_cols[0]
                df_family[total_col] = pd.to_numeric(df_family[total_col], errors='coerce')
                df_family = df_family.dropna(subset=[total_col])
                
                # Display data
                st.dataframe(df_family, use_container_width=True)
                
                # Global map
                st.markdown("## Global Map – Patent Family Filings")
                
                # Simple country code mapping
                df_family_map = df_family.copy()
                country_col = df_family_map.columns[0]
                
                # Create a simple mapping for major countries
                country_map = {
                    'US': 'USA', 'CN': 'CHN', 'JP': 'JPN', 'DE': 'DEU', 'KR': 'KOR',
                    'GB': 'GBR', 'FR': 'FRA', 'CA': 'CAN', 'AU': 'AUS', 'IT': 'ITA',
                    'ES': 'ESP', 'NL': 'NLD', 'SE': 'SWE', 'CH': 'CHE', 'NO': 'NOR',
                    'FI': 'FIN', 'DK': 'DNK', 'BE': 'BEL', 'AT': 'AUT', 'EP': 'EUR',
                    'WO': 'WORLD'
                }
                
                df_family_map['iso_alpha3'] = df_family_map[country_col].map(country_map)
                df_family_valid = df_family_map[df_family_map['iso_alpha3'].notna()]
                
                if not df_family_valid.empty:
                    fig_world = px.choropleth(
                        df_family_valid,
                        locations='iso_alpha3',
                        color=total_col,
                        hover_name=country_col,
                        hover_data={total_col: True},
                        color_continuous_scale="OrRd",
                        projection="natural earth",
                        title="Patent Family Filings by Country"
                    )
                    
                    st.plotly_chart(fig_world, use_container_width=True)
                
                # Nordic Analysis
                st.subheader("Nordic Data – Patent Family Filings")
                
                NORDIC_COUNTRY_CODES = ['NO', 'SE', 'FI', 'DK', 'IS']
                df_nordic = df_family[df_family[country_col].isin(NORDIC_COUNTRY_CODES)].copy()
                
                # Add missing Nordic countries with 0 values
                existing = df_nordic[country_col].tolist()
                missing = [code for code in NORDIC_COUNTRY_CODES if code not in existing]
                
                for code in missing:
                    new_row = {country_col: code, total_col: 0}
                    df_nordic = pd.concat([df_nordic, pd.DataFrame([new_row])], ignore_index=True)
                
                st.dataframe(df_nordic, use_container_width=True)
                
                # Nordic map
                st.subheader("Nordic Map – Patent Family Filings")
                
                df_nordic['iso_alpha3'] = df_nordic[country_col].map(country_map)
                
                fig_nordic = px.choropleth(
                    df_nordic,
                    locations='iso_alpha3',
                    color=total_col,
                    hover_name=country_col,
                    hover_data={total_col: True},
                    color_continuous_scale="OrRd",
                    scope="europe",
                    projection="natural earth",
                    title="Nordic Patent Family Filings"
                )
                
                fig_nordic.update_layout(height=600)
                st.plotly_chart(fig_nordic, use_container_width=True)
                
                # Nordic bar chart
                st.subheader("Patent Family Filings by Nordic Country")
                
                df_nordic_sorted = df_nordic.sort_values(total_col, ascending=True)
                
                fig_nordic_bar = px.bar(
                    df_nordic_sorted,
                    x=total_col,
                    y=country_col,
                    orientation='h',
                    title="Patent Family Filings by Nordic Country",
                    color=total_col,
                    color_continuous_scale="Blues"
                )
                
                fig_nordic_bar.update_layout(height=400)
                st.plotly_chart(fig_nordic_bar, use_container_width=True)
                
                # Bar chart
                st.subheader("Patent Family Filings by Country")
                
                df_sorted = df_family.sort_values(total_col, ascending=True)
                
                fig_bar = px.bar(
                    df_sorted.tail(20),
                    x=total_col,
                    y=country_col,
                    orientation='h',
                    title="Patent Family Filings by Country",
                    color=total_col,
                    color_continuous_scale="Viridis"
                )
                
                fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
                st.plotly_chart(fig_bar, use_container_width=True)
        
    with tab2:
        st.subheader("Priority Countries Analysis")
        
        if 'priority_country' in data and not data['priority_country'].empty:
            df_priority = data['priority_country'].dropna()
            df_priority['Total'] = pd.to_numeric(df_priority['Total'], errors='coerce')
            df_priority = df_priority.dropna()
            
            st.dataframe(df_priority, use_container_width=True)
            
            # Global map
            st.markdown("## Global Map – Priority Countries")
            
            # Country mapping for priority data
            country_map = {
                'US': 'USA', 'CN': 'CHN', 'JP': 'JPN', 'DE': 'DEU', 'KR': 'KOR',
                'GB': 'GBR', 'FR': 'FRA', 'CA': 'CAN', 'AU': 'AUS', 'IT': 'ITA',
                'ES': 'ESP', 'NL': 'NLD', 'SE': 'SWE', 'CH': 'CHE', 'NO': 'NOR',
                'FI': 'FIN', 'DK': 'DNK', 'BE': 'BEL', 'AT': 'AUT', 'EP': 'EUR'
            }
            
            df_priority['iso_alpha3'] = df_priority['Priority Country'].map(country_map)
            df_priority_map = df_priority[df_priority['iso_alpha3'].notna()]
            non_standard = df_priority[df_priority['iso_alpha3'].isna()]
            
            fig_world = px.choropleth(
                df_priority_map,
                locations='iso_alpha3',
                color='Total',
                hover_name='Priority Country',
                hover_data={'Total': True},
                color_continuous_scale="Purples",
                projection="natural earth",
                title="Priority Filings by Country"
            )
            
            # Add annotation for non-standard codes
            if not non_standard.empty:
                legend_text = "Non-standard codes:<br>"
                for _, row in non_standard.iterrows():
                    legend_text += f"{row['Priority Country']}: {int(row['Total'])}<br>"
                
                fig_world.add_annotation(
                    text=legend_text,
                    xref="paper", yref="paper",
                    x=0, y=0,
                    showarrow=False,
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor="black",
                    borderwidth=1,
                    font=dict(size=10),
                    align="left",
                    xanchor="left", yanchor="bottom"
                )
            
            st.plotly_chart(fig_world, use_container_width=True)
            
            # Nordic Analysis
            st.subheader("Nordic Data – Priority Countries")
            
            NORDIC_COUNTRY_CODES = ['NO', 'SE', 'FI', 'DK', 'IS']
            df_nordic = df_priority[df_priority['Priority Country'].isin(NORDIC_COUNTRY_CODES)].copy()
            
            # Add missing Nordic countries
            existing = df_nordic['Priority Country'].tolist()
            missing = [code for code in NORDIC_COUNTRY_CODES if code not in existing]
            
            for code in missing:
                iso3_code = country_map.get(code, code)
                new_row = {
                    'Priority Country': code,
                    'Total': 0,
                    'iso_alpha3': iso3_code
                }
                df_nordic = pd.concat([df_nordic, pd.DataFrame([new_row])], ignore_index=True)
            
            st.dataframe(df_nordic[['Priority Country', 'Total']], use_container_width=True)
            
            # Nordic map
            st.subheader("Nordic Map – Priority Countries")
            
            fig_nordic = px.choropleth(
                df_nordic,
                locations='iso_alpha3',
                color='Total',
                hover_name='Priority Country',
                hover_data={'Total': True},
                color_continuous_scale="Purples",
                scope="europe",
                projection="natural earth",
                title="Nordic Priority Filings"
            )
            
            fig_nordic.update_layout(height=600)
            st.plotly_chart(fig_nordic, use_container_width=True)
            
            # Nordic bar chart
            st.subheader("Priority Filings by Nordic Country")
            
            df_nordic_sorted = df_nordic.sort_values('Total', ascending=True)
            
            fig_nordic_bar = px.bar(
                df_nordic_sorted,
                x='Total',
                y='Priority Country',
                orientation='h',
                title="Priority Filings by Nordic Country",
                color='Total',
                color_continuous_scale="Greens"
            )
            
            fig_nordic_bar.update_layout(height=400)
            st.plotly_chart(fig_nordic_bar, use_container_width=True)
            
            # Bar chart
            st.subheader("Priority Filings by Country")
            
            df_sorted = df_priority.sort_values('Total', ascending=True)
            
            fig_bar = px.bar(
                df_sorted.tail(20),
                x='Total',
                y='Priority Country',
                orientation='h',
                title="Priority Filings by Country",
                color='Total',
                color_continuous_scale="Plasma"
            )
            
            fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
            st.plotly_chart(fig_bar, use_container_width=True)

def show_entity_analysis(data):
    """Entity Analysis with Assignees and Inventors tabs"""
    
    st.title("Entity Analysis")
    
    # Create tabs
    tab1, tab2 = st.tabs(["🏢 Assignees", "👨‍💼 Inventors"])
    
    with tab1:
        st.title("Assignee Analysis")
        
        if 'assignee_data' in data and not data['assignee_data'].empty:
            df = data['assignee_data']
            
            st.markdown("### Top 15 Assignees/Applicants and Country of Origin by Patent Count")
            st.markdown("*This analysis shows the leading patent assignees and their countries of origin, providing insights into global innovation leadership and patent filing strategies.*")
            st.dataframe(df, use_container_width=True)
            
            # Validate required columns
            if "Count" not in df.columns:
                st.error("Column 'Count' missing from dataset.")
                return
            
            # Top 15 assignees chart
            df_top = df.nlargest(15, "Count").copy()
            df_top = df_top.sort_values("Count", ascending=True)
            
            df_top["Label"] = df_top["Country"].fillna("") + " - " + df_top["Assignee"]
            
            st.markdown("### Top 15 Assignees/Applicants and Country of Origin by Patent Count")
            st.markdown("*This chart visualizes the patent portfolio distribution among leading assignees, highlighting which organizations hold the most patents in the dataset.*")
            
            fig = px.bar(
                df_top,
                x="Count",
                y="Label",
                orientation="h",
                color="Count",
                title="Top Assignees",
                color_continuous_scale="OrRd",
            )
            
            fig.update_layout(
                height=500,
                xaxis_title="Patent Count",
                yaxis_title="Assignee",
                yaxis={"categoryorder": "total ascending"},
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.title("Inventor Analysis")
        
        if 'inventor_data' in data and not data['inventor_data'].empty:
            df = data['inventor_data']
            
            st.markdown("### Top Inventors and Country of Origin by Patent Count")
            st.markdown("*This analysis identifies the most prolific inventors and their countries of origin, showcasing individual innovation contributions to the patent landscape.*")
            st.dataframe(df, use_container_width=True)
            
            # Validate required columns
            if "Count" not in df.columns:
                st.error("Column 'Count' missing from dataset.")
                return
            
            # Top inventors chart
            df_top = df.nlargest(15, "Count").copy()
            df_top = df_top.sort_values("Count", ascending=True)
            
            df_top["Label"] = df_top["Country"].fillna("") + " - " + df_top["Inventor"]
            
            st.markdown("### Top Inventors and Country of Origin by Patent Count")
            st.markdown("*This chart displays the most active inventors, providing insights into individual innovation leadership and geographical distribution of inventive talent.*")
            
            fig = px.bar(
                df_top,
                x="Count",
                y="Label",
                orientation="h",
                color="Count",
                title="Top Inventors",
                color_continuous_scale="Blues",
            )
            
            fig.update_layout(
                height=500,
                xaxis_title="Patent Count",
                yaxis_title="Inventor",
                yaxis={"categoryorder": "total ascending"},
            )
            
            st.plotly_chart(fig, use_container_width=True)

def show_timeline_analysis(data):
    """Timeline Analysis from processed data"""
    
    st.title("Timeline Analysis - Current Owner")
    
    # Show temporal data if available
    if 'timeline_owner' in data and not data['timeline_owner'].empty:
        df_temporal = data['timeline_owner']
        
        # Timeline by top current owners (similar to main_app.py)
        st.markdown("### Timeline by Top Current Owners")
        st.markdown("*This chart shows patent application trends by current patent owners over time.*")
        
        # Convert pivot table data to long format for timeline analysis
        owner_col = df_temporal.columns[0]  # First column is owner names
        year_columns = [col for col in df_temporal.columns[1:] if str(col).replace('.', '').isdigit()]
        
        # Convert to long format
        df_timeline_list = []
        for idx, row in df_temporal.iterrows():
            owner = row[owner_col]
            if pd.isna(owner) or owner == "" or str(owner).lower() in ['none', 'nan', 'null']:
                continue
                
            for year_col in year_columns:
                count = row[year_col]
                try:
                    count = pd.to_numeric(count, errors='coerce')
                    year = int(float(year_col))
                    if pd.isna(count) or count <= 0 or year < 2010 or year > 2025:
                        continue
                        
                    df_timeline_list.append({
                        'Current Owner': str(owner).strip(),
                        'Year': year,
                        'Count': int(count)
                    })
                except:
                    continue
        
        if df_timeline_list:
            df_timeline = pd.DataFrame(df_timeline_list)
            
            # Clean owner names and get top 8 owners
            df_timeline['Current Owner'] = df_timeline['Current Owner'].str.replace('"', '').str.strip()
            df_timeline = df_timeline[~df_timeline['Current Owner'].str.lower().isin(['none', 'nan', 'null', ''])]
            
            top_owners = df_timeline.groupby('Current Owner')['Count'].sum().nlargest(8).index.tolist()
            df_timeline_top = df_timeline[df_timeline['Current Owner'].isin(top_owners)].copy()
            
            # Group by year and owner
            timeline_by_owner = df_timeline_top.groupby(['Year', 'Current Owner'])['Count'].sum().reset_index()
            
            if not timeline_by_owner.empty:
                min_year = max(2010, timeline_by_owner['Year'].min())
                max_year = min(2025, timeline_by_owner['Year'].max())
                
                st.markdown(f"### Timeline Analysis ({int(min_year)} - {int(max_year)})")
                
                fig_timeline = px.line(
                    timeline_by_owner,
                    x='Year',
                    y='Count',
                    color='Current Owner',
                    title=f'Patent Applications Timeline by Top Current Owners ({int(min_year)} - {int(max_year)})',
                    markers=True,
                    line_shape='linear'
                )
                
                fig_timeline.update_traces(line=dict(width=2), marker=dict(size=6))
                
                fig_timeline.update_layout(
                    xaxis_title="Year",
                    yaxis_title="Number of Patent Applications",
                    height=600,
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left", 
                        x=1.01
                    ),
                    xaxis=dict(
                        tickmode='linear',
                        tick0=min_year,
                        dtick=1
                    )
                )
                
                st.plotly_chart(fig_timeline, use_container_width=True)
                
                # Add note about incomplete 2025 data
                st.info("📝 **Note:** The apparent decline in patent applications towards the end of 2025 is likely due to incomplete data, as not all patent applications for that year have been published yet. Patent publication typically occurs 18 months after the filing date.")
                
                # Show summary data table
                st.markdown("#### Data Summary for Timeline")
                summary_table = timeline_by_owner.pivot(index='Year', columns='Current Owner', values='Count').fillna(0)
                st.dataframe(summary_table, use_container_width=True)
            else:
                st.warning("No timeline data available after filtering")
        else:
            st.warning("No valid timeline data found")
    else:
        st.info("Timeline analysis data not available")

def show_classification_analysis(data):
    """IPC and CPC Classification Analysis"""
    
    st.title("IPC and CPC Classification Analysis")
    
    # Educational explanation
    st.info("""
    **Why Patents Have Multiple Classifications:**
    
    A single patent application often covers multiple classification codes because modern inventions typically involve several related technologies or technical areas. For example:
    
    - A **quantum computer patent** might include classifications for: quantum computing (G06N), semiconductor devices (H01L), and data processing (G06F)
    - A **medical device patent** might span: diagnostic equipment (A61B), data analysis (G06F), and wireless communication (H04L)
    
    This multi-classification approach ensures patents are discoverable by researchers working in any of the related technical fields and reflects the interdisciplinary nature of modern innovation.
    """)
    
    # IPC Analysis
    st.markdown("## IPC (International Patent Classification) Analysis")
    
    if 'ipc_data' in data and not data['ipc_data'].empty:
        ipc_summary = data['ipc_data']
        
        # Display class descriptions
        st.markdown("**IPC Classification Descriptions:**")
        class_columns = ipc_summary.columns[2:].tolist()
        for col_code in class_columns:
            st.markdown(f"- **{col_code}**: Patent classification code")
        st.markdown("")
        
        st.markdown("### Top 15 Current Owners - Top 5 IPC Classifications")
        st.dataframe(ipc_summary, use_container_width=True)
        
        # IPC Visualizations
        st.markdown("### IPC Visualizations")
        
        # Grouped bar chart
        st.markdown("#### Grouped Bar Chart - Top Companies by IPC Classification")
        
        if len(ipc_summary.columns) > 2:
            class_cols = ipc_summary.columns[2:].tolist()
            df_chart = ipc_summary.head(8)
            
            fig = go.Figure()
            colors = px.colors.qualitative.Set3
            
            for i, col in enumerate(class_cols):
                fig.add_trace(go.Bar(
                    name=col,
                    x=df_chart['Current Owner'],
                    y=df_chart[col],
                    marker_color=colors[i % len(colors)],
                    text=df_chart[col],
                    textposition='auto'
                ))
            
            fig.update_layout(
                title='Top 8 Companies - IPC Patent Distribution',
                xaxis_title='Current Owner',
                yaxis_title='Number of Patents',
                barmode='group',
                height=500,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        # Heatmap
        st.markdown("#### Heatmap - IPC Activity Matrix")
        
        if len(ipc_summary.columns) > 2:
            class_cols = ipc_summary.columns[2:].tolist()
            heatmap_data = ipc_summary[['Current Owner'] + class_cols].set_index('Current Owner')
            
            fig = px.imshow(
                heatmap_data.values,
                labels=dict(x="Classification", y="Current Owner", color="Patents"),
                x=class_cols,
                y=heatmap_data.index,
                color_continuous_scale='Blues',
                aspect='auto'
            )
            
            fig.update_layout(
                title='IPC Patent Activity Heatmap',
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # CPC Analysis
    st.markdown("## CPC (Cooperative Patent Classification) Analysis")
    
    if 'cpc_data' in data and not data['cpc_data'].empty:
        cpc_summary = data['cpc_data']
        
        # Display class descriptions
        st.markdown("**CPC Classification Descriptions:**")
        class_columns = cpc_summary.columns[2:].tolist()
        for col_code in class_columns:
            st.markdown(f"- **{col_code}**: Patent classification code")
        st.markdown("")
        
        st.markdown("### Top 15 Current Owners - Top 5 CPC Classifications")
        st.dataframe(cpc_summary, use_container_width=True)
        
        # CPC Visualizations
        st.markdown("### CPC Visualizations")
        
        # Grouped bar chart
        st.markdown("#### Grouped Bar Chart - Top Companies by CPC Classification")
        
        if len(cpc_summary.columns) > 2:
            class_cols = cpc_summary.columns[2:].tolist()
            df_chart = cpc_summary.head(8)
            
            fig = go.Figure()
            colors = px.colors.qualitative.Pastel1
            
            for i, col in enumerate(class_cols):
                fig.add_trace(go.Bar(
                    name=col,
                    x=df_chart['Current Owner'],
                    y=df_chart[col],
                    marker_color=colors[i % len(colors)],
                    text=df_chart[col],
                    textposition='auto'
                ))
            
            fig.update_layout(
                title='Top 8 Companies - CPC Patent Distribution',
                xaxis_title='Current Owner',
                yaxis_title='Number of Patents',
                barmode='group',
                height=500,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap
        st.markdown("#### Heatmap - CPC Activity Matrix")
        
        if len(cpc_summary.columns) > 2:
            class_cols = cpc_summary.columns[2:].tolist()
            heatmap_data = cpc_summary[['Current Owner'] + class_cols].set_index('Current Owner')
            
            fig = px.imshow(
                heatmap_data.values,
                labels=dict(x="Classification", y="Current Owner", color="Patents"),
                x=class_cols,
                y=heatmap_data.index,
                color_continuous_scale='Greens',
                aspect='auto'
            )
            
            fig.update_layout(
                title='CPC Patent Activity Heatmap',
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)

def show_methods_2_3_analysis_display():
    """Methods 2/3 Analysis for display_data.py"""
    from app.Methods_2_3_Analysis import show_methods_2_3_analysis
    show_methods_2_3_analysis()

def show_norway_analysis(data):
    """Norway Analysis (placeholder)"""
    
    st.title("Norway Patent Analysis")
    
    st.markdown("""
    **Analysis of Norwegian Patent Records**
    
    This analysis examines Norwegian patent activity in this specific technology class,
    showing limited domestic innovation and foreign applicant dominance.
    """)
    
    # Simple analysis
    st.markdown("## Norway Patent Activity Analysis")
    
    st.warning("""
    **Limited Norwegian Patent Activity:**
    - Only **3 patent applications** identified  
    - Limited domestic innovation in this specific technology area
    - Most patent activity comes from foreign applicants filing in Norway
    """)
    
    # Key observations
    st.markdown("### Key Observations (Data Only)")
    
    st.info("""
    The data shows 3 patent applications in Norway within this technology class.
    
    Most of these applications are filed by non-Norwegian applicants.
    
    This indicates low domestic filing activity in this class based on the available data.
    """)

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    # Patent Landscape Analysis

    Explore patent filing trends across regions, assignees, and jurisdictions.

    **About This Analysis:** This patent landscape analysis is designed to provide insights and examples of analytical approaches specifically for Class G06N10 (quantum computing technologies). This is just a draft before final analysis.
    """)
    
    # Load data
    with st.spinner("Loading data..."):
        data = load_all_data()
    
    if not data:
        st.error("No data files found. Please ensure processed CSV files are available.")
        return
    
    # Navigation
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
    
    # Show selected page
    if "Geographic Patent Analysis" in page:
        show_geographic_analysis(data)
    elif "Entity Analysis" in page:
        show_entity_analysis(data)
    elif "Timeline Analysis" in page:
        show_timeline_analysis(data)
    elif "Classification Analysis: IPC/CPC Codes" in page:
        show_classification_analysis(data)
    elif "Methods 2/3 Analysis" in page:
        show_methods_2_3_analysis_display()
    elif "Norway Analysis" in page:
        show_norway_analysis(data)

if __name__ == "__main__":
    main()