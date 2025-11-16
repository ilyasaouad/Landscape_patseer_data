#!/usr/bin/env python3
"""
Norway Analysis
Comprehensive analysis of Norway's patent landscape across all data sources.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_paths import raw, processed


def show_norway_analysis_tab():
    """
    Analysis of Norwegian patent records from Norsk_data.xlsx
    """
    
    st.title("Norway Patent Analysis")
    
    # Introduction
    st.markdown("""
    **Analysis of Norwegian Patent Records**
    
    This analysis examines Norwegian patent activity in this specific technology class,
    showing limited domestic innovation and foreign applicant dominance.
    """)
    
    # Load Norwegian patent records
    norway_data = load_norsk_data_only()
    
    if not norway_data:
        st.error("Unable to load Norwegian patent records from Norsk_data.xlsx")
        return
    
    # Create analysis of the Norwegian records
    create_norsk_records_analysis(norway_data)


def load_norsk_data_only():
    """
    Load only the Norwegian patent records from Norsk_data.xlsx
    """
    
    norway_data = {}
    
    try:
        st.markdown("### Loading Norwegian Patent Records...")
        
        with st.spinner("Loading Norsk_data.xlsx..."):
            norsk_file = raw("Norsk_data.xlsx")
            if norsk_file.exists():
                df_norsk = pd.read_excel(norsk_file)
                norway_data['norsk_records'] = df_norsk
                st.success(f"Successfully loaded {len(df_norsk)} Norwegian patent records")
            else:
                st.error("Norsk_data.xlsx not found in data/raw/")
                return {}
        
        return norway_data
        
    except Exception as e:
        st.error(f"Error loading Norwegian patent records: {e}")
        return {}


def check_file_exists(filename):
    """Check if file exists in raw data folder."""
    try:
        file_path = raw(filename)
        return file_path.exists()
    except:
        return False


def load_classification_data(filename):
    """Load classification data with special handling for CPC-Full format."""
    try:
        file_path = raw(filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Parse CSV data
        import csv
        from io import StringIO
        header_line = lines[0].strip()
        header_reader = csv.reader(StringIO(header_line))
        headers = next(header_reader)
        
        # Parse data rows
        data_rows = []
        max_cols = len(headers)
        
        for line in lines[2:]:  # Skip header and separator line
            line = line.strip()
            if line and not line.startswith('Current Owner'):
                try:
                    row_reader = csv.reader(StringIO(line))
                    row = next(row_reader)
                    if len(row) >= 2:
                        # Pad or trim row to match header length
                        if len(row) < max_cols:
                            row.extend([''] * (max_cols - len(row)))
                        elif len(row) > max_cols:
                            row = row[:max_cols]
                        data_rows.append(row)
                except:
                    continue
        
        if data_rows:
            df = pd.DataFrame(data_rows, columns=headers)
            return df
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Error loading {filename}: {e}")
        return pd.DataFrame()


def filter_norway_entities(df):
    """Filter entities that contain Norway-related keywords."""
    if df.empty:
        return df
    
    norway_keywords = ['NORWAY', 'NORSK', 'NORWEGIAN', 'NORGE', 'OSLO', 'BERGEN', 'TRONDHEIM', 'STAVANGER', 
                      'NTNU', 'UIO', 'SINTEF', 'NFR', 'TELENOR', 'EQUINOR', 'STATOIL', 'NORCEM']
    
    owner_col = df.columns[0]
    mask = df[owner_col].str.upper().str.contains('|'.join(norway_keywords), na=False)
    return df[mask]


def load_temporal_classification_data():
    """Load temporal CPC classification data."""
    try:
        file_path = raw("Application-Year _CPC-Full.csv")
        # Similar parsing logic as in IPC_CPC_class.py
        # Return processed temporal data
        return pd.DataFrame()  # Placeholder for now
    except:
        return pd.DataFrame()


def load_timeline_data(file_path):
    """Load timeline data from CSV."""
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
        return df
    except:
        return pd.DataFrame()


def filter_norway_timeline(df):
    """Filter timeline data for Norwegian entities."""
    if df.empty:
        return df
    
    norway_keywords = ['NORWAY', 'NORSK', 'NORWEGIAN', 'NORGE', 'OSLO', 'BERGEN', 'TRONDHEIM', 
                      'STAVANGER', 'NTNU', 'UIO', 'SINTEF', 'TELENOR', 'EQUINOR', 'STATOIL']
    
    # Check if current owner column exists
    if 'Current Owner' in df.columns:
        mask = df['Current Owner'].str.upper().str.contains('|'.join(norway_keywords), na=False)
        return df[mask]
    return pd.DataFrame()


def create_geographic_analysis(norway_data):
    """Create geographic analysis of Norway's patent presence."""
    
    st.markdown("## 🗺️ Geographic Patent Presence")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Priority Filings (Originating in Norway)")
        if 'priority' in norway_data and not norway_data['priority'].empty:
            priority_data = norway_data['priority']
            st.dataframe(priority_data, use_container_width=True)
            
            if 'Total' in priority_data.columns:
                total_priority = priority_data['Total'].sum()
                st.metric("Total Priority Patents", f"{total_priority:,}")
        else:
            st.info("No Norway priority data found")
    
    with col2:
        st.markdown("### Family Filings (Filed in Norway)")
        if 'family' in norway_data and not norway_data['family'].empty:
            family_data = norway_data['family']
            st.dataframe(family_data, use_container_width=True)
            
            if 'Total' in family_data.columns:
                total_family = family_data['Total'].sum()
                st.metric("Total Family Patents", f"{total_family:,}")
        else:
            st.info("No Norway family data found")
    
    # Nordic comparison if data available
    create_nordic_comparison(norway_data)


def create_nordic_comparison(norway_data):
    """Create comparison with other Nordic countries."""
    
    st.markdown("### 🇳🇴🇸🇪🇫🇮🇩🇰 Nordic Countries Comparison")
    
    try:
        # Load Nordic data for comparison
        priority_file = raw("Priority_Country_Map.csv")
        df_priority = pd.read_csv(priority_file, encoding="utf-8").dropna()
        
        # Use the first column as country column
        country_col = df_priority.columns[0]
        nordic_countries = ['NO', 'SE', 'FI', 'DK', 'IS']
        nordic_data = df_priority[df_priority[country_col].isin(nordic_countries)]
        
        if not nordic_data.empty and 'Total' in nordic_data.columns:
            nordic_data['Total'] = pd.to_numeric(nordic_data['Total'], errors='coerce')
            
            fig = px.bar(
                nordic_data,
                x=country_col,
                y='Total',
                title='Nordic Countries - Priority Patent Filings',
                color='Total',
                color_continuous_scale='Blues'
            )
            
            fig.update_layout(
                xaxis_title="Nordic Country",
                yaxis_title="Number of Priority Patents",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Norway's rank
            norway_rank = nordic_data.sort_values('Total', ascending=False).reset_index(drop=True)
            norway_position = norway_rank[norway_rank[country_col] == 'NO'].index
            if len(norway_position) > 0:
                rank = norway_position[0] + 1
                st.info(f"🏆 Norway ranks #{rank} among Nordic countries in priority patents")
        
    except Exception as e:
        st.warning(f"Could not create Nordic comparison: {e}")


def create_entity_analysis(norway_data):
    """Analyze Norwegian innovation entities."""
    
    st.markdown("## 🏢 Norwegian Innovation Entities")
    
    # Current owners analysis
    if 'current_owners' in norway_data and not norway_data['current_owners'].empty:
        st.markdown("### Top Norwegian Current Patent Holders")
        owners_df = norway_data['current_owners']
        
        # Clean and process data
        owner_col = owners_df.columns[0]
        total_col = owners_df.columns[1]
        
        # Convert total to numeric
        owners_df[total_col] = pd.to_numeric(owners_df[total_col], errors='coerce')
        owners_df = owners_df.dropna(subset=[total_col])
        owners_df = owners_df.sort_values(total_col, ascending=False)
        
        # Display top 10
        top_owners = owners_df.head(10)
        st.dataframe(top_owners[[owner_col, total_col]], use_container_width=True)
        
        # Visualization
        if len(top_owners) > 0:
            fig = px.bar(
                top_owners,
                x=total_col,
                y=owner_col,
                orientation='h',
                title='Top Norwegian Patent Holders',
                color=total_col,
                color_continuous_scale='Greens'
            )
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Assignees analysis
    if 'assignees' in norway_data and not norway_data['assignees'].empty:
        st.markdown("### Norwegian Assignees")
        assignee_data = norway_data['assignees']
        st.dataframe(assignee_data, use_container_width=True)
    
    # Inventors analysis
    if 'inventors' in norway_data and not norway_data['inventors'].empty:
        st.markdown("### Norwegian Inventors")
        inventor_data = norway_data['inventors']
        st.dataframe(inventor_data, use_container_width=True)


def create_technology_analysis(norway_data):
    """Analyze Norwegian technology focus areas."""
    
    st.markdown("## 🔬 Norwegian Technology Focus Areas")
    
    if 'current_owners' in norway_data and not norway_data['current_owners'].empty:
        owners_df = norway_data['current_owners']
        
        # Get classification columns (skip owner and total)
        class_cols = owners_df.columns[2:].tolist()
        
        if class_cols:
            # Calculate total patents per classification across all Norwegian entities
            tech_totals = {}
            for col in class_cols:
                col_data = pd.to_numeric(owners_df[col], errors='coerce').fillna(0)
                tech_totals[col] = col_data.sum()
            
            # Sort and get top technologies
            tech_sorted = sorted(tech_totals.items(), key=lambda x: x[1], reverse=True)
            top_technologies = tech_sorted[:10]  # Top 10
            
            if top_technologies:
                st.markdown("### Top Technology Areas for Norwegian Entities")
                
                # Create dataframe for visualization
                tech_df = pd.DataFrame(top_technologies, columns=['Technology', 'Patents'])
                
                # Clean technology names
                tech_df['Technology_Clean'] = tech_df['Technology'].apply(
                    lambda x: x.split(':')[0] if ':' in str(x) else str(x)
                )
                
                st.dataframe(tech_df[['Technology_Clean', 'Patents']], use_container_width=True)
                
                # Visualization
                fig = px.bar(
                    tech_df,
                    x='Patents',
                    y='Technology_Clean',
                    orientation='h',
                    title='Norwegian Technology Focus Areas',
                    color='Patents',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Technology analysis requires current owner classification data")


def create_temporal_analysis(norway_data):
    """Analyze Norwegian patent trends over time."""
    
    st.markdown("## 📈 Temporal Innovation Patterns")
    
    if 'timeline' in norway_data and not norway_data['timeline'].empty:
        timeline_df = norway_data['timeline']
        
        st.markdown("### Norwegian Patent Activity Over Time")
        st.dataframe(timeline_df, use_container_width=True)
        
        # If timeline data has year columns, create trend analysis
        year_columns = [col for col in timeline_df.columns if col.isdigit()]
        
        if year_columns:
            # Aggregate by year
            yearly_totals = {}
            for year_col in year_columns:
                year_data = pd.to_numeric(timeline_df[year_col], errors='coerce').fillna(0)
                yearly_totals[int(year_col)] = year_data.sum()
            
            # Create trend visualization
            years = sorted(yearly_totals.keys())
            totals = [yearly_totals[year] for year in years]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=years,
                y=totals,
                mode='lines+markers',
                name='Norwegian Patents',
                line=dict(color='red', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title='Norwegian Patent Filings Trend',
                xaxis_title='Year',
                yaxis_title='Number of Patents',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Temporal analysis requires timeline data")


def create_strategic_insights(norway_data):
    """Generate strategic insights about Norwegian patent landscape."""
    
    st.markdown("## 🎯 Strategic Insights")
    
    insights = []
    
    # Geographic insights
    if 'priority' in norway_data and not norway_data['priority'].empty:
        priority_total = norway_data['priority']['Total'].sum() if 'Total' in norway_data['priority'].columns else 0
        insights.append(f"🌍 **Geographic Presence**: Norway has {priority_total:,} priority patents")
    
    # Entity insights
    if 'current_owners' in norway_data and not norway_data['current_owners'].empty:
        num_entities = len(norway_data['current_owners'])
        insights.append(f"🏢 **Innovation Ecosystem**: {num_entities} Norwegian patent-holding entities identified")
    
    # Technology insights
    if 'current_owners' in norway_data and not norway_data['current_owners'].empty:
        class_cols = norway_data['current_owners'].columns[2:].tolist()
        active_techs = 0
        for col in class_cols:
            if pd.to_numeric(norway_data['current_owners'][col], errors='coerce').sum() > 0:
                active_techs += 1
        insights.append(f"🔬 **Technology Breadth**: Active in {active_techs} different technology classifications")
    
    # Display insights
    if insights:
        for insight in insights:
            st.success(insight)
    
    st.markdown("""
    ### 📊 Analysis Summary
    
    **Norway's Patent Landscape Characteristics:**
    - **Innovation Focus**: Technology areas where Norway shows strength
    - **Global Position**: Norway's role in international patent filings  
    - **Ecosystem Players**: Mix of commercial entities, research institutions, and individual inventors
    - **Temporal Patterns**: Evolution of Norwegian innovation over time
    
    **Note**: This analysis is based on available data sources and provides insights into Norway's 
    position in the global patent landscape across different dimensions.
    """)


def create_norsk_records_analysis(norway_data):
    """
    Analyze Norway's limited patent activity in this technology class
    """
    
    st.markdown("## Norway Patent Activity Analysis")
    
    if 'norsk_records' not in norway_data or norway_data['norsk_records'].empty:
        st.info("Norwegian patent data not available")
        return
    
    df_norsk = norway_data['norsk_records']
    
    st.markdown("### Limited Norwegian Patent Activity")
    st.warning(f"""
    **Norway shows minimal patent activity in this technology class:**
    - Only **{len(df_norsk)} patent applications** identified
    - Limited domestic innovation in this specific technology area
    - Most patent activity comes from foreign applicants filing in Norway
    """)
    
    # Show the few Norwegian records
    st.markdown("### Norwegian Patent Records")
    st.dataframe(df_norsk, use_container_width=True)
    
    # Analyze assignees and origins
    st.markdown("### Analysis of Patent Origins")
    
    if 'Assignee' in df_norsk.columns and not df_norsk.empty:
        # Check for Norwegian vs foreign assignees
        norwegian_indicators = ['NORWAY', 'NORSK', 'NORWEGIAN', 'NORGE', 'NO', 'OSLO', 'BERGEN', 
                               'TRONDHEIM', 'STAVANGER', 'NTNU', 'SINTEF', 'UIO']
        
        norwegian_patents = 0
        foreign_patents = 0
        assignee_origins = {}
        
        for idx, row in df_norsk.iterrows():
            assignee = str(row['Assignee']) if pd.notna(row['Assignee']) else ""
            
            # Check if assignee appears to be Norwegian
            is_norwegian = any(indicator in assignee.upper() for indicator in norwegian_indicators)
            
            if is_norwegian:
                norwegian_patents += 1
                assignee_origins[assignee] = "Norwegian"
            else:
                foreign_patents += 1
                # Try to identify country from assignee name
                if 'INC' in assignee.upper() or 'CORP' in assignee.upper() or 'LLC' in assignee.upper():
                    assignee_origins[assignee] = "US (likely)"
                elif 'LTD' in assignee.upper() or 'LIMITED' in assignee.upper():
                    assignee_origins[assignee] = "UK/Commonwealth (likely)"
                elif 'GMBH' in assignee.upper():
                    assignee_origins[assignee] = "German (likely)"
                elif 'AB' in assignee.upper():
                    assignee_origins[assignee] = "Swedish (likely)"
                else:
                    assignee_origins[assignee] = "Foreign (unspecified)"
        
        # Display findings
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Norwegian Assignees", norwegian_patents)
            st.metric("Foreign Assignees", foreign_patents)
        
        with col2:
            if foreign_patents > norwegian_patents:
                st.write("Data shows foreign applicant activity")
            else:
                st.success("Norwegian presence in technology")
        
        # Show assignee breakdown
        st.markdown("### Assignee Origin Analysis")
        
        origin_df = pd.DataFrame(list(assignee_origins.items()), columns=['Assignee', 'Origin'])
        st.dataframe(origin_df, use_container_width=True)
        
        # Country summary
        if len(origin_df) > 0:
            origin_counts = origin_df['Origin'].value_counts()
            
            st.markdown("### Country/Origin Summary")
            
            for origin, count in origin_counts.items():
                if 'Norwegian' in origin:
                    st.success(f"Norwegian {origin}: {count} patent(s)")
                else:
                    st.info(f"Foreign {origin}: {count} patent(s)")
    
    # Key observations
    st.markdown("### Key Observations (Data Only)")
    
    st.info(f"""
    The data shows {len(df_norsk)} patent applications in Norway within this technology class.
    
    Most of these applications are filed by non-Norwegian applicants.
    
    This indicates low domestic filing activity in this class based on the available data.
    """)
    
    
    # Simple visualization if there's data
    if len(df_norsk) > 0 and 'Assignee' in df_norsk.columns:
        assignee_counts = df_norsk['Assignee'].value_counts()
        
        st.markdown("### Patent Distribution by Assignee")
        
        fig = px.pie(
            values=assignee_counts.values,
            names=assignee_counts.index,
            title=f'Distribution of {len(df_norsk)} Patents by Assignee'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    show_norway_analysis_tab()