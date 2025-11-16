#!/usr/bin/env python3
"""
Timeline Current Owner Count Analysis
Displays patent filings over time by current owner.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.file_paths import raw


def show_timeline_current_owner_tab():
    """
    Streamlit UI for Timeline Current Owner Analysis.
    Displays patent filing trends over time by current owner.
    """
    
    st.title("Timeline Analysis - Current Owner")
    
    file_path = raw("Innovation_Timeline_(Current_Owner_-_Application_Date).csv")
    
    try:
        # Load the data - this is a pivot table format
        df_raw = pd.read_csv(file_path, encoding="utf-8")
        
        # Clean display data - replace None values with empty strings
        df_display = df_raw.head(10).copy()
        df_display = df_display.fillna("")
        df_display = df_display.replace(['None', 'none', 'NONE'], "")
        
        # Display retrieved data
        st.markdown("### Retrieved Data for Timeline Analysis")
        st.dataframe(df_display, use_container_width=True)
        
        # Convert pivot table to long format
        df_clean = prepare_timeline_data_from_pivot(df_raw)
        
        if not df_clean.empty:
            # Create visualizations
            create_timeline_visualizations(df_clean)
        else:
            st.error("No valid data found after processing")
            
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
    except Exception as e:
        st.error(f"Error loading timeline data: {e}")


def prepare_timeline_data_from_pivot(df_pivot):
    """
    Convert pivot table format to long format for visualization.
    Input: DataFrame with owners as rows and years as columns
    Output: DataFrame with columns: Current Owner, Year, Count
    """
    try:
        # First column contains the owner names
        owner_col = df_pivot.columns[0]
        
        # Get year columns (skip first column which is owner names)
        year_columns = [col for col in df_pivot.columns[1:] if str(col).isdigit()]
        
        # Convert to long format
        df_long_list = []
        
        for idx, row in df_pivot.iterrows():
            owner = row[owner_col]
            if pd.isna(owner) or owner == "" or str(owner).lower() in ['none', 'nan', 'null']:
                continue
                
            for year_col in year_columns:
                count = row[year_col]
                
                # Convert count to numeric, skip if not valid
                try:
                    count = pd.to_numeric(count, errors='coerce')
                    if pd.isna(count) or count <= 0:
                        continue
                        
                    df_long_list.append({
                        'Current Owner': str(owner).strip(),
                        'Year': int(year_col),
                        'Count': int(count)
                    })
                except:
                    continue
        
        # Create DataFrame
        df_clean = pd.DataFrame(df_long_list)
        
        if not df_clean.empty:
            # Filter reasonable years
            df_clean = df_clean[(df_clean['Year'] >= 2000) & (df_clean['Year'] <= 2030)]
            
            # Clean owner names (remove quotes, extra spaces, filter out None/null)
            df_clean['Current Owner'] = df_clean['Current Owner'].str.replace('"', '').str.strip()
            df_clean = df_clean[~df_clean['Current Owner'].str.lower().isin(['none', 'nan', 'null', ''])]
            df_clean = df_clean[df_clean['Current Owner'] != 'None']
            
            # Group by owner and year in case of duplicates
            df_clean = df_clean.groupby(['Current Owner', 'Year'])['Count'].sum().reset_index()
        
        return df_clean
        
    except Exception as e:
        st.error(f"Error converting pivot data: {e}")
        return pd.DataFrame()


def create_timeline_visualizations(df):
    """
    Create timeline visualizations for current owner data.
    """
    
    # 1. Overall timeline - patents per year
    st.markdown("### Patent Applications Over Time")
    st.markdown("*This chart shows the total number of patent applications across all current owners in the dataset by year.*")
    
    yearly_counts = df.groupby('Year')['Count'].sum().reset_index()
    
    fig_timeline = px.line(
        yearly_counts,
        x='Year',
        y='Count',
        title='Total Patent Applications by Year (All Current Owners)',
        markers=True
    )
    
    fig_timeline.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Patent Applications",
        height=400
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # 2. Timeline by top owners
    st.markdown("### Timeline by Top Current Owners")
    
    # Get top 8 owners for better visibility
    top_owners = df['Current Owner'].value_counts().head(8).index.tolist()
    df_top = df[df['Current Owner'].isin(top_owners)].copy()
    
    # Aggregate data properly (df already has Count column)
    timeline_by_owner = df_top.groupby(['Year', 'Current Owner'])['Count'].sum().reset_index()
    
    # Ensure we have data to plot
    if not timeline_by_owner.empty and len(timeline_by_owner) > 0:
        fig_owner_timeline = px.line(
            timeline_by_owner,
            x='Year',
            y='Count',
            color='Current Owner',
            title='Patent Applications Timeline by Top Current Owners',
            markers=True,
            line_shape='linear'
        )
        
        fig_owner_timeline.update_traces(line=dict(width=2), marker=dict(size=6))
        
        fig_owner_timeline.update_layout(
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
                tick0=timeline_by_owner['Year'].min(),
                dtick=1
            )
        )
        
        st.plotly_chart(fig_owner_timeline, use_container_width=True)
        
        # Show data table for verification
        st.markdown("#### Data Summary for Timeline")
        summary_table = timeline_by_owner.pivot(index='Year', columns='Current Owner', values='Count').fillna(0)
        st.dataframe(summary_table, use_container_width=True)
    else:
        st.error("No data available for timeline visualization")
    
    # 4. Heatmap of applications by year and top owners
    st.markdown("### Patent Activity Heatmap")
    
    if not df_top.empty:
        # Create pivot table for heatmap using the Count column
        heatmap_data = df_top.groupby(['Year', 'Current Owner'])['Count'].sum().unstack(fill_value=0)
        
        if not heatmap_data.empty and heatmap_data.shape[0] > 0 and heatmap_data.shape[1] > 0:
            fig_heatmap = px.imshow(
                heatmap_data.T,  # Transpose so owners are on y-axis
                aspect='auto',
                title='Patent Applications Heatmap (Top Owners)',
                color_continuous_scale='Blues',
                labels=dict(x="Year", y="Current Owner", color="Applications")
            )
            
            fig_heatmap.update_layout(
                height=500,
                xaxis=dict(side="bottom"),
                yaxis=dict(side="left")
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.warning("Insufficient data for heatmap visualization")
    else:
        st.warning("No data available for heatmap")
    
    # Patent data insights
    st.markdown("### About This Patent Data")
    st.markdown("""
    This timeline analysis shows patent application trends by current patent owners over time. 
    The data represents the innovation activity and patent filing strategies of different organizations, 
    helping to identify leading innovators and emerging trends in the patent landscape.
    
    **Key Insights:**
    - Patent filing patterns can indicate R&D investment cycles
    - Timeline trends may reflect market opportunities and technological developments  
    - Current owner data shows post-filing patent ownership (including acquisitions/transfers)
    """)


if __name__ == "__main__":
    show_timeline_current_owner_tab()