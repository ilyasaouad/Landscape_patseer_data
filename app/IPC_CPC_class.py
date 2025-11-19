#!/usr/bin/env python3
"""
IPC and CPC Classification Analysis
Analyzes patent classification data for current owners.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Optional NetworkX import for network graphs
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_paths import raw, processed


def show_ipc_cpc_classification_tab():
    """
    Streamlit UI for IPC and CPC Classification Analysis.
    Shows top 15 current owners with their top 3 classification codes.
    """
    
    st.title("IPC and CPC Classification Analysis")
    
    # Classification Descriptions
    st.markdown("### Classification Descriptions")
    st.markdown("""
    **IPC Classification Descriptions:**
    - **G06N10/40**: Patent classification code for both IPCs and CPCs
    
    **CPC Classification Descriptions:**  
    - **G06N10/40**: Patent classification code for both IPCs and CPCs
    """)
    
    # Total Records Analysis using IPC_Full.csv and CPC_Full.csv
    st.markdown("### 📊 Total Records Analysis")
    
    try:
        # Load IPC_Full.csv 
        ipc_file = "data/raw/IPC_Full.csv"
        if os.path.exists(ipc_file):
            df_ipc_full = pd.read_csv(ipc_file)
            
            st.markdown("#### 📋 Top 10 IPC Classifications")
            
            # Show first 10 rows as table
            ipc_top_10 = df_ipc_full.head(10)
            st.dataframe(ipc_top_10, use_container_width=True)
            
            # Create vertical bar chart from the first 10 rows
            if 'Total' in ipc_top_10.columns:
                
                # Sort by Total values (descending - largest first) - use original values
                ipc_top_10_sorted = ipc_top_10.sort_values('Total', ascending=False, key=lambda x: pd.to_numeric(x.astype(str).str.replace(',',''), errors='coerce'))
                
                # Get classification names (first column) and shorten them
                class_col = ipc_top_10_sorted.columns[0]
                
                # Create shortened labels (class code + first 3 words of description)
                def shorten_classification(text):
                    if ':' in str(text):
                        parts = str(text).split(':', 1)
                        class_code = parts[0].strip()
                        description = parts[1].strip() if len(parts) > 1 else ''
                        desc_words = description.split()[:3]  # First 3 words
                        short_desc = ' '.join(desc_words)
                        return f"{class_code}: {short_desc}" if short_desc else class_code
                    return str(text)
                
                ipc_top_10_sorted['Short_Label'] = ipc_top_10_sorted[class_col].apply(shorten_classification)
                
                # Create horizontal bar chart with different color for each bar
                fig_ipc = px.bar(
                    ipc_top_10_sorted,
                    x='Total',
                    y='Short_Label',
                    title='Top 10 IPC Classifications',
                    color='Total',
                    color_continuous_scale='viridis',
                    orientation='h'
                )
                
                fig_ipc.update_layout(
                    height=600,
                    xaxis_title="Total Records",
                    yaxis_title="IPC Classification",
                    showlegend=False,
                    yaxis={'autorange': 'reversed'}
                )
                
                fig_ipc.update_traces(
                    text=ipc_top_10_sorted['Total'],
                    textposition='outside',
                    textfont_size=12
                )
                
                st.plotly_chart(fig_ipc, use_container_width=True)
            else:
                st.warning("'Total' column not found in IPC_Full.csv")
        else:
            st.warning("IPC_Full.csv not found")
            
        # Load CPC_Full.csv
        cpc_file = "data/raw/CPC_Full.csv"
        if os.path.exists(cpc_file):
            df_cpc_full = pd.read_csv(cpc_file)
            
            st.markdown("#### 🏷️ Top 10 CPC Classifications")
            
            # Show first 10 rows as table
            cpc_top_10 = df_cpc_full.head(10)
            st.dataframe(cpc_top_10, use_container_width=True)
            
            # Create vertical bar chart from the first 10 rows
            if 'Total' in cpc_top_10.columns:
                
                # Sort by Total values (descending - largest first) - use original values
                cpc_top_10_sorted = cpc_top_10.sort_values('Total', ascending=False, key=lambda x: pd.to_numeric(x.astype(str).str.replace(',',''), errors='coerce'))
                
                # Get classification names (should be "CPC Full" column)
                class_col = 'CPC Full' if 'CPC Full' in cpc_top_10_sorted.columns else cpc_top_10_sorted.columns[0]
                
                # Create shortened labels (class code + first 3 words of description)
                def shorten_classification(text):
                    if ':' in str(text):
                        parts = str(text).split(':', 1)
                        class_code = parts[0].strip()
                        description = parts[1].strip() if len(parts) > 1 else ''
                        desc_words = description.split()[:3]  # First 3 words
                        short_desc = ' '.join(desc_words)
                        return f"{class_code}: {short_desc}" if short_desc else class_code
                    return str(text)
                
                cpc_top_10_sorted['Short_Label'] = cpc_top_10_sorted[class_col].apply(shorten_classification)
                
                # Create horizontal bar chart with different color for each bar
                fig_cpc = px.bar(
                    cpc_top_10_sorted,
                    x='Total',
                    y='Short_Label',
                    title='Top 10 CPC Classifications',
                    color='Total',
                    color_continuous_scale='plasma',
                    orientation='h'
                )
                
                fig_cpc.update_layout(
                    height=600,
                    xaxis_title="Total Records",
                    yaxis_title="CPC Classification",
                    showlegend=False,
                    yaxis={'autorange': 'reversed'}
                )
                
                fig_cpc.update_traces(
                    text=cpc_top_10_sorted['Total'],
                    textposition='outside',
                    textfont_size=12
                )
                
                st.plotly_chart(fig_cpc, use_container_width=True)
            else:
                st.warning("'Total' column not found in CPC_Full.csv")
        else:
            st.warning("CPC_Full.csv not found")
            
    except Exception as e:
        st.warning(f"Could not load IPC/CPC full data files: {e}")
        st.info("Please ensure IPC_Full.csv and CPC_Full.csv files are available in data/raw/")
    
    st.markdown("---")
    
    # Educational explanation about patent classifications
    st.info("""
    **💡 Why Patents Have Multiple Classifications:**
    
    A single patent application often covers multiple classification codes because modern inventions typically involve several related technologies or technical areas. For example:
    
    - A **quantum computer patent** might include classifications for: quantum computing (G06N), semiconductor devices (H01L), and data processing (G06F)
    - A **medical device patent** might span: diagnostic equipment (A61B), data analysis (G06F), and wireless communication (H04L)
    
    This multi-classification approach ensures patents are discoverable by researchers working in any of the related technical fields and reflects the interdisciplinary nature of modern innovation.
    """)
    
    # Load and process IPC data
    st.markdown("## IPC (International Patent Classification) Analysis")
    ipc_summary = create_classification_summary("Current-Owner_IPC-Full.csv", "IPC")
    
    if ipc_summary is not None:
        st.markdown("### Top 15 Current Owners - Top 5 IPC Classifications")
        
        # Display classification descriptions
        display_class_descriptions(ipc_summary, "IPC")
        
        st.dataframe(ipc_summary, use_container_width=True)
        
        # Save to CSV
        save_classification_data(ipc_summary, "Top_IPC_Assignee_Count.csv")
        
        # Add visualizations
        create_classification_visualizations(ipc_summary, "IPC")
    
    # Load and process CPC data
    st.markdown("## CPC (Cooperative Patent Classification) Analysis") 
    cpc_summary = create_classification_summary("Current-Owner_CPC-Full.csv", "CPC")
    
    if cpc_summary is not None:
        st.markdown("### Top 15 Current Owners - Top 5 CPC Classifications")
        
        # Display classification descriptions
        display_class_descriptions(cpc_summary, "CPC")
        
        st.dataframe(cpc_summary, use_container_width=True)
        
        # Save to CSV
        save_classification_data(cpc_summary, "Top_CPC_Assignee_Count.csv")
        
        # Add visualizations
        create_classification_visualizations(cpc_summary, "CPC")
        
        # Add temporal analysis for CPC
        create_temporal_analysis(cpc_summary, "CPC")


def create_classification_summary(filename, classification_type):
    """
    Load and clean the classification data, showing top 15 owners with all classification columns.
    Returns the original dataframe structure with all classification codes.
    """
    
    file_path = raw(filename)
    
    try:
        # Special handling for IPC-Full.csv format
        if "IPC-Full" in filename:
            # Read the raw file and manually parse the CSV structure
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Extract header from first line (contains the classification codes)
            header_line = lines[0].strip()
            # Parse header manually - split by commas but handle quoted strings
            import csv
            from io import StringIO
            header_reader = csv.reader(StringIO(header_line))
            headers = next(header_reader)
            
            # Parse data rows (skip line 1 which has separators)
            data_rows = []
            max_cols = len(headers)
            
            for line in lines[2:]:  # Skip header and separator line
                line = line.strip()
                if line and not line.startswith('Current Owner'):
                    try:
                        row_reader = csv.reader(StringIO(line))
                        row = next(row_reader)
                        if len(row) >= 2:  # At least owner and total
                            # Pad or trim row to match header length
                            if len(row) < max_cols:
                                row.extend([''] * (max_cols - len(row)))
                            elif len(row) > max_cols:
                                row = row[:max_cols]
                            data_rows.append(row)
                    except:
                        continue
            
            # Create dataframe
            if data_rows:
                df = pd.DataFrame(data_rows, columns=headers)
            else:
                st.error("No valid data rows found in IPC file")
                return None
            
        else:
            # Normal CSV loading for CPC files
            df = pd.read_csv(file_path, encoding="utf-8")
            # Remove header rows (first 2 rows contain headers)  
            df = df.iloc[2:].copy()
        
        # Get owner and total columns
        owner_col = df.columns[0]
        total_col = df.columns[1]
        
        # Clean owner names (remove quotes)
        df[owner_col] = df[owner_col].astype(str).str.replace('"', '').str.strip()
        
        # Convert Total column to numeric
        df[total_col] = df[total_col].astype(str).str.replace('"', '')
        df[total_col] = pd.to_numeric(df[total_col], errors='coerce')
        df = df.dropna(subset=[total_col])
        
        # Convert all classification columns to numeric
        for col in df.columns[2:]:  # Skip owner and total columns
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Find top 5 classification columns by total count across all companies
        class_cols = df.columns[2:]  # Skip owner and total columns
        class_totals = df[class_cols].sum().sort_values(ascending=False)
        top_5_classifications = class_totals.head(5).index.tolist()
        
        # Get top 15 current owners
        top_15_owners = df.nlargest(15, total_col)
        
        # Select only the required columns: Current Owner, Total, and top 5 classifications
        selected_columns = [owner_col, total_col] + top_5_classifications
        display_df = top_15_owners[selected_columns].copy()
        
        # Create clean column names - extract just the classification codes
        column_renames = {
            owner_col: 'Current Owner',
            total_col: 'Total'
        }
        
        for col in top_5_classifications:
            if ':' in str(col):
                code_part = col.split(':')[0].strip().replace('"', '')
                column_renames[col] = code_part
            else:
                column_renames[col] = str(col).replace('"', '')
        
        display_df = display_df.rename(columns=column_renames)
        
        return display_df
        
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        st.error(f"Error loading {classification_type} data: {e}")
        return None


def display_class_descriptions(df, classification_type):
    """
    Display the classification descriptions at the top of the dataframe.
    """
    # Get the classification columns (skip Current Owner and Total)
    class_columns = df.columns[2:]
    
    st.markdown(f"**{classification_type} Classification Descriptions:**")
    
    # Load original data to get full descriptions
    filename = f"Current-Owner_{classification_type}-Full.csv"
    file_path = raw(filename)
    
    try:
        original_df = pd.read_csv(file_path, encoding="utf-8")
        
        # Find matching columns in original data
        for col_code in class_columns:
            # Find the original column with full description
            matching_cols = [col for col in original_df.columns if col.startswith(col_code)]
            if matching_cols:
                full_description = matching_cols[0]
                if ':' in full_description:
                    desc_part = full_description.split(':', 1)[1].strip()
                    # Clean up formatting issues
                    desc_part = desc_part.replace('""', '').replace('"', '').strip()
                    # Remove trailing semicolons and extra spaces
                    desc_part = desc_part.rstrip(';').strip()
                    
                    # Check if description is just repeating the code
                    if desc_part and desc_part != col_code and not desc_part.startswith(col_code):
                        st.markdown(f"- **{col_code}**: {desc_part}")
                    else:
                        st.markdown(f"- **{col_code}**: Patent classification code")
                else:
                    st.markdown(f"- **{col_code}**: {full_description}")
            else:
                st.markdown(f"- **{col_code}**: Patent classification code")
        
        st.markdown("")  # Add spacing
        
    except:
        # Fallback if we can't load descriptions
        for col_code in class_columns:
            st.markdown(f"- **{col_code}**: Patent classification")
        st.markdown("")


def save_classification_data(df, filename):
    """
    Save the classification dataframe to processed data folder.
    """
    try:
        output_path = processed(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding="utf-8")
        # File saved silently - no UI message needed
    except Exception as e:
        st.error(f"Error saving {filename}: {e}")


def create_classification_visualizations(df, classification_type):
    """
    Create visualizations for the classification data.
    """
    
    st.markdown(f"### {classification_type} Visualizations")
    
    # 1. Grouped Bar Chart
    st.markdown(f"#### 1. Grouped Bar Chart - Top Companies by {classification_type} Classification")
    create_grouped_bar_chart(df, classification_type)
    
    # 2. Heatmap
    st.markdown(f"#### 2. Heatmap - {classification_type} Activity Matrix")
    create_heatmap(df, classification_type)
    
    # 3. Network Node Graph
    st.markdown(f"#### 3. Network Graph - Company-Classification Relationships")
    create_network_graph(df, classification_type)
    
    # 4. Example Analysis
    st.markdown(f"#### 4. Example Analysis - Top Company")
    create_example_analysis(df, classification_type)


def create_grouped_bar_chart(df, classification_type):
    """
    Create a grouped bar chart showing top companies across classifications.
    """
    
    # Get classification columns (skip Current Owner and Total)
    class_cols = df.columns[2:].tolist()
    
    # Prepare data for grouped bar chart - take top 8 companies
    df_chart = df.head(8)
    
    fig = go.Figure()
    
    # Add a bar for each classification
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
        title=f'Top 8 Companies - {classification_type} Patent Distribution',
        xaxis_title='Current Owner',
        yaxis_title='Number of Patents',
        barmode='group',
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_heatmap(df, classification_type):
    """
    Create a heatmap showing patent activity across companies and classifications.
    """
    
    # Get classification columns (skip Current Owner and Total)
    class_cols = df.columns[2:].tolist()
    
    # Prepare data for heatmap - use all 15 companies
    heatmap_data = df[['Current Owner'] + class_cols].set_index('Current Owner')
    
    # Create heatmap
    fig = px.imshow(
        heatmap_data.values,
        labels=dict(x="Classification", y="Current Owner", color="Patents"),
        x=class_cols,
        y=heatmap_data.index,
        color_continuous_scale='Blues',
        aspect='auto'
    )
    
    fig.update_layout(
        title=f'{classification_type} Patent Activity Heatmap',
        height=600,
        xaxis_title=f'{classification_type} Classifications',
        yaxis_title='Current Owners'
    )
    
    # Add text annotations
    for i, row in enumerate(heatmap_data.values):
        for j, value in enumerate(row):
            if value > 0:
                fig.add_annotation(
                    x=j, y=i,
                    text=str(int(value)),
                    showarrow=False,
                    font=dict(color="white" if value > heatmap_data.values.max()/2 else "black")
                )
    
    st.plotly_chart(fig, use_container_width=True)


def create_network_graph(df, classification_type):
    """
    Create a network graph showing relationships between companies and classifications.
    """
    
    if not NETWORKX_AVAILABLE:
        st.warning("NetworkX not installed. Install with: pip install networkx")
        st.info("Network graph visualization is not available.")
        return
    
    try:
        # Create network graph
        G = nx.Graph()
        
        # Get classification columns (skip Current Owner and Total)
        class_cols = df.columns[2:].tolist()
        
        # Add nodes for companies and classifications
        companies = df['Current Owner'].head(8).tolist()  # Top 8 companies for clarity
        
        # Add company nodes
        for company in companies:
            G.add_node(company, node_type='company', size=50)
        
        # Add classification nodes
        for classification in class_cols:
            G.add_node(classification, node_type='classification', size=30)
        
        # Add edges based on patent counts
        for _, row in df.head(8).iterrows():
            company = row['Current Owner']
            for classification in class_cols:
                patent_count = row[classification]
                if patent_count > 0:
                    # Edge weight based on patent count
                    weight = patent_count / 10  # Scale down for visualization
                    G.add_edge(company, classification, weight=weight, patents=patent_count)
        
        # Calculate positions using spring layout
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Extract coordinates
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_info.append(f"{edge[0]} - {edge[1]}: {G[edge[0]][edge[1]]['patents']} patents")
        
        # Create enhanced edge traces with hover info
        edge_traces = []
        
        # Group edges by company for better visualization
        company_colors = px.colors.qualitative.Set3
        
        for i, company in enumerate(companies):
            company_edge_x = []
            company_edge_y = []
            company_edge_info = []
            
            # Get edges for this specific company
            for edge in G.edges():
                if edge[0] == company:  # Company to classification edge
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    company_edge_x.extend([x0, x1, None])
                    company_edge_y.extend([y0, y1, None])
                    patents = G[edge[0]][edge[1]]['patents']
                    company_edge_info.append(f"{edge[0]} → {edge[1]}: {patents} patents")
            
            if company_edge_x:  # Only create trace if there are edges
                edge_trace = go.Scatter(
                    x=company_edge_x, y=company_edge_y,
                    line=dict(width=2, color=company_colors[i % len(company_colors)]),
                    hoverinfo='text',
                    hovertext=company_edge_info,
                    mode='lines',
                    name=f'{company} connections',
                    showlegend=False,
                    opacity=0.7
                )
                edge_traces.append(edge_trace)
        
        # Create node traces
        company_x = [pos[node][0] for node in companies if node in pos]
        company_y = [pos[node][1] for node in companies if node in pos]
        company_names = [node for node in companies if node in pos]
        
        class_x = [pos[node][0] for node in class_cols if node in pos]
        class_y = [pos[node][1] for node in class_cols if node in pos]
        class_names = [node for node in class_cols if node in pos]
        
        # Create enhanced hover information for companies
        company_hover_text = []
        for company in company_names:
            # Get connected classifications for this company
            row_data = df[df['Current Owner'] == company].iloc[0]
            connected_classes = []
            for classification in class_cols:
                count = row_data[classification]
                if count > 0:
                    connected_classes.append(f"{classification}: {count} patents")
            
            hover_info = f"<b>{company}</b><br>" + "<br>".join(connected_classes)
            company_hover_text.append(hover_info)
        
        # Company nodes with enhanced hover
        company_trace = go.Scatter(
            x=company_x, y=company_y,
            mode='markers+text',
            marker=dict(
                size=25, 
                color='lightblue', 
                line=dict(width=2, color='darkblue'),
                sizemode='diameter'
            ),
            text=[name.replace(' ', '<br>') if len(name) > 15 else name for name in company_names],
            textposition="middle center",
            textfont=dict(size=8),
            hoverinfo='text',
            hovertext=company_hover_text,
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            name='Companies',
            customdata=company_names  # For potential click handling
        )
        
        # Create enhanced hover for classifications
        class_hover_text = []
        for classification in class_names:
            # Get companies using this classification
            using_companies = []
            for _, row in df.head(8).iterrows():
                company = row['Current Owner']
                count = row[classification]
                if count > 0:
                    using_companies.append(f"{company}: {count} patents")
            
            hover_info = f"<b>{classification}</b><br>" + "<br>".join(using_companies)
            class_hover_text.append(hover_info)
        
        # Classification nodes with enhanced hover
        class_trace = go.Scatter(
            x=class_x, y=class_y,
            mode='markers+text',
            marker=dict(
                size=18, 
                color='lightcoral', 
                line=dict(width=2, color='darkred'),
                sizemode='diameter'
            ),
            text=[name.replace('/', '<br>') if '/' in name else name for name in class_names],
            textposition="middle center",
            textfont=dict(size=7),
            hoverinfo='text',
            hovertext=class_hover_text,
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            name='Classifications'
        )
        
        # Create figure with all traces
        all_traces = edge_traces + [company_trace, class_trace]
        fig = go.Figure(data=all_traces,
                       layout=go.Layout(
                           title=dict(
                               text=f'{classification_type} Network: Company-Classification Relationships',
                               font=dict(size=16)
                           ),
                           showlegend=True,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="💡 Hover over nodes to see patent details. Each company's connections are color-coded.",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor='left', yanchor='bottom',
                               font=dict(size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           height=600
                       ))
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.warning(f"Network graph could not be created: {e}")
        st.info("Install networkx with: pip install networkx")


def create_example_analysis(df, classification_type):
    """
    Create a simple example analysis of the top company's patent classification profile.
    """
    
    # Get the top company (first row)
    top_company_data = df.iloc[0]
    company_name = top_company_data['Current Owner']
    total_patents = top_company_data['Total']
    
    # Get classification columns and their counts
    class_cols = df.columns[2:].tolist()
    company_classes = []
    
    for classification in class_cols:
        count = top_company_data[classification]
        if count > 0:
            company_classes.append((classification, count))
    
    # Sort by patent count
    company_classes.sort(key=lambda x: x[1], reverse=True)
    
    # Create example analysis
    st.markdown("**📋 Example Analysis (Not Deep Analysis)**")
    
    st.info(f"""
    **Company:** {company_name}  
    **Total Patents:** {total_patents}
    
    **Top Classification Areas:**
    """)
    
    # Show top classifications with simple analysis
    analysis_text = f"**{company_name}** shows patent activity across **{len(company_classes)}** different {classification_type} classifications:\n\n"
    
    for i, (classification, count) in enumerate(company_classes, 1):
        percentage = (count / total_patents) * 100
        analysis_text += f"**{i}. {classification}**: {count} patents ({percentage:.1f}% of portfolio)\n\n"
    
    st.markdown(analysis_text)
    
    # Simple interpretation
    if company_classes:
        top_class, top_count = company_classes[0]
        top_percentage = (top_count / total_patents) * 100
        
        st.markdown("**📊 Simple Interpretation:**")
        
        if top_percentage > 50:
            focus_level = "highly concentrated"
        elif top_percentage > 30:
            focus_level = "moderately focused"
        else:
            focus_level = "diversified"
            
        st.success(f"""
        **{company_name}** has a **{focus_level}** patent portfolio with **{top_percentage:.1f}%** of patents in **{top_class}**.
        
        **Pattern:** The company shows {"strong specialization" if top_percentage > 50 else "moderate diversification" if len(company_classes) > 2 else "focused innovation"} across {len(company_classes)} classification areas.
        """)
        
    st.warning("""
    **⚠️ Note:** This is a basic example analysis showing how to interpret classification connections. A NOT comprehensive analysis.
    """)


def create_temporal_analysis(df, classification_type):
    """
    Create temporal analysis showing classification trends over time.
    """
    
    if classification_type != "CPC":
        return  # Only do this for CPC data
    
    st.markdown("### 5. Temporal Analysis - CPC Classifications Over Time")
    
    try:
        # Load the Application-Year CPC-Full data
        temporal_file = raw("Application-Year _CPC-Full.csv")
        
        # Read the temporal data with similar parsing as before
        with open(temporal_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Extract header from first line
        import csv
        from io import StringIO
        header_line = lines[0].strip()
        header_reader = csv.reader(StringIO(header_line))
        headers = next(header_reader)
        
        # Parse data rows (skip line 1 which has separators)
        data_rows = []
        max_cols = len(headers)
        
        for line in lines[2:]:  # Skip header and separator line
            line = line.strip()
            if line and not line.startswith('Application Year'):
                try:
                    row_reader = csv.reader(StringIO(line))
                    row = next(row_reader)
                    if len(row) >= 2:  # At least year and total
                        # Pad or trim row to match header length
                        if len(row) < max_cols:
                            row.extend([''] * (max_cols - len(row)))
                        elif len(row) > max_cols:
                            row = row[:max_cols]
                        data_rows.append(row)
                except:
                    continue
        
        if not data_rows:
            st.error("No valid temporal data found")
            return
        
        # Create temporal dataframe
        df_temporal = pd.DataFrame(data_rows, columns=headers)
        
        # Clean data
        year_col = df_temporal.columns[0]
        total_col = df_temporal.columns[1]
        
        # Convert year and total to numeric
        df_temporal[year_col] = df_temporal[year_col].astype(str).str.replace('"', '').str.strip()
        df_temporal[total_col] = df_temporal[total_col].astype(str).str.replace('"', '')
        df_temporal[year_col] = pd.to_numeric(df_temporal[year_col], errors='coerce')
        df_temporal[total_col] = pd.to_numeric(df_temporal[total_col], errors='coerce')
        
        # Remove rows with invalid years
        df_temporal = df_temporal.dropna(subset=[year_col, total_col])
        df_temporal = df_temporal[(df_temporal[year_col] >= 2000) & (df_temporal[year_col] <= 2030)]
        
        # Convert classification columns to numeric
        for col in df_temporal.columns[2:]:
            df_temporal[col] = pd.to_numeric(df_temporal[col], errors='coerce').fillna(0).astype(int)
        
        # Get the top 5 CPC classifications from the main analysis
        top_5_classes = df.columns[2:].tolist()  # Get the same 5 classifications
        
        # Filter temporal data to only include these top 5 classifications
        available_classes = []
        for top_class in top_5_classes:
            # Find matching column in temporal data
            matching_cols = [col for col in df_temporal.columns[2:] if col.startswith(top_class.split(':')[0]) or top_class.split(':')[0] in col]
            if matching_cols:
                available_classes.append(matching_cols[0])
        
        if not available_classes:
            st.warning("No matching CPC classifications found in temporal data")
            return
        
        # Create the final dataframe with Year + Top 5 CPC classes
        temporal_analysis_cols = [year_col] + available_classes[:5]  # Limit to top 5
        df_temporal_final = df_temporal[temporal_analysis_cols].copy()
        
        # Rename year column for clarity
        df_temporal_final = df_temporal_final.rename(columns={year_col: 'Application Year'})
        
        # Display class descriptions for temporal analysis
        st.markdown("**CPC Classification Descriptions:**")
        class_columns_for_desc = df_temporal_final.columns[1:].tolist()
        
        # Load original CPC data to get descriptions
        try:
            cpc_full_file = raw("Current-Owner_CPC-Full.csv")
            with open(cpc_full_file, 'r', encoding='utf-8') as f:
                cpc_lines = f.readlines()
            
            import csv
            from io import StringIO
            cpc_header_line = cpc_lines[0].strip()
            cpc_header_reader = csv.reader(StringIO(cpc_header_line))
            cpc_headers = next(cpc_header_reader)
            
            for col_code in class_columns_for_desc:
                code_part = col_code.split(':')[0].strip() if ':' in col_code else col_code
                matching_cols = [col for col in cpc_headers if col.startswith(code_part)]
                if matching_cols:
                    full_description = matching_cols[0]
                    if ':' in full_description:
                        desc_part = full_description.split(':', 1)[1].strip()
                        desc_part = desc_part.replace('""', '').replace('"', '').strip().rstrip(';').strip()
                        if desc_part and desc_part != code_part and not desc_part.startswith(code_part):
                            st.markdown(f"- **{code_part}**: {desc_part}")
                        else:
                            st.markdown(f"- **{code_part}**: Patent classification code")
                    else:
                        st.markdown(f"- **{code_part}**: Patent classification code")
                else:
                    st.markdown(f"- **{code_part}**: Patent classification code")
            
            st.markdown("")
        except:
            # Fallback if descriptions can't be loaded
            for col_code in class_columns_for_desc:
                code_part = col_code.split(':')[0].strip() if ':' in col_code else col_code
                st.markdown(f"- **{code_part}**: Patent classification code")
            st.markdown("")
        
        # Clean column names to show only classification codes
        df_temporal_display = df_temporal_final.copy()
        column_renames = {'Application Year': 'Application Year'}
        
        for col in df_temporal_final.columns[1:]:
            if ':' in col:
                code_part = col.split(':')[0].strip()
                column_renames[col] = code_part
            else:
                column_renames[col] = col
        
        df_temporal_display = df_temporal_display.rename(columns=column_renames)
        
        # Filter to 2010-2025 range
        df_temporal_final['Application Year'] = pd.to_numeric(df_temporal_final['Application Year'], errors='coerce')
        df_temporal_final = df_temporal_final.dropna(subset=['Application Year'])
        df_temporal_final = df_temporal_final[
            (df_temporal_final['Application Year'] >= 2010) & 
            (df_temporal_final['Application Year'] <= 2025)
        ]
        
        # Update display dataframe with same filter
        df_temporal_display['Application Year'] = pd.to_numeric(df_temporal_display['Application Year'], errors='coerce')
        df_temporal_display = df_temporal_display.dropna(subset=['Application Year'])
        df_temporal_display = df_temporal_display[
            (df_temporal_display['Application Year'] >= 2010) & 
            (df_temporal_display['Application Year'] <= 2025)
        ]
        
        # Sort by year from small to big
        df_temporal_display = df_temporal_display.sort_values('Application Year').reset_index(drop=True)
        df_temporal_final = df_temporal_final.sort_values('Application Year').reset_index(drop=True)
        
        # Display the temporal dataframe
        st.markdown("#### CPC Classifications vs Application Year")
        st.dataframe(df_temporal_display, use_container_width=True)
        
        # Save temporal analysis
        save_classification_data(df_temporal_final, "CPC_Classifications_vs_Year.csv")
        
        # Create temporal visualization
        st.markdown("#### Temporal Trends - Line Chart")
        
        # Prepare data for plotting
        year_column = 'Application Year'
        class_columns = df_temporal_final.columns[1:].tolist()
        
        fig = go.Figure()
        colors = px.colors.qualitative.Set3
        
        for i, classification in enumerate(class_columns):
            # Clean classification name for legend
            clean_name = classification.split(':')[0] if ':' in classification else classification
            
            fig.add_trace(go.Scatter(
                x=df_temporal_final[year_column],
                y=df_temporal_final[classification],
                mode='lines+markers',
                name=clean_name,
                line=dict(width=3, color=colors[i % len(colors)]),
                marker=dict(size=6),
                hovertemplate=f'<b>{clean_name}</b><br>' +
                             'Year: %{x}<br>' +
                             'Patents: %{y}<extra></extra>'
            ))
        
        fig.update_layout(
            title='CPC Classification Trends Over Time (2010-2025)',
            xaxis_title='Application Year',
            yaxis_title='Number of Patent Applications',
            height=600,
            width=1200,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                tickmode='linear',
                tick0=2010,
                dtick=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add note about incomplete 2025 data
        st.info("📝 **Note:** The apparent decline in patent applications towards the end of 2025 is likely due to incomplete data, as not all patent applications for that year have been published yet. Patent publication typically occurs 18 months after the filing date.")
        
        # Simple trend analysis
        st.markdown("#### Temporal Insights")
        
        # Calculate growth/decline for each classification
        insights = []
        for classification in class_columns:
            clean_name = classification.split(':')[0] if ':' in classification else classification
            recent_years = df_temporal_final[df_temporal_final[year_column] >= df_temporal_final[year_column].max() - 2]
            older_years = df_temporal_final[df_temporal_final[year_column] <= df_temporal_final[year_column].max() - 5]
            
            if len(recent_years) > 0 and len(older_years) > 0:
                recent_avg = recent_years[classification].mean()
                older_avg = older_years[classification].mean()
                
                if recent_avg > older_avg * 1.2:
                    trend = "📈 Growing"
                elif recent_avg < older_avg * 0.8:
                    trend = "📉 Declining"
                else:
                    trend = "📊 Stable"
                
                insights.append(f"**{clean_name}**: {trend}")
        
        if insights:
            st.success("**Technology Trends:**\n\n" + "\n\n".join(insights))
        
    except FileNotFoundError:
        st.error("Application-Year_CPC-Full.csv file not found in data/raw/")
    except Exception as e:
        st.error(f"Error processing temporal data: {e}")


def load_and_process_classification_data(filename, classification_type):
    """
    Load and process IPC or CPC classification data.
    Returns top 20 current owners by total patent count.
    """
    
    file_path = raw(filename)
    
    try:
        # Load the data
        df = pd.read_csv(file_path, encoding="utf-8")
        
        # Clean the data - skip header rows and get proper columns
        owner_col = df.columns[0]
        total_col = df.columns[1]
        
        # Remove header rows (first 2 rows contain headers)
        df_clean = df.iloc[2:].copy()
        
        # Convert Total column to numeric
        df_clean[total_col] = pd.to_numeric(df_clean[total_col], errors='coerce')
        df_clean = df_clean.dropna(subset=[total_col])
        
        # Get top 20 current owners
        top_20_owners = df_clean.nlargest(20, total_col)
        
        return top_20_owners
        
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        st.error(f"Error loading {classification_type} data: {e}")
        return None


def get_top3_owners_top3_classes(df, classification_type):
    """
    For top 3 current owners, get their top 3 classification codes.
    """
    
    if df is None or len(df) == 0:
        return {}
    
    # Get top 3 owners
    top_3_owners = df.head(3)
    owner_col = df.columns[0]
    total_col = df.columns[1]
    
    results = {}
    
    for idx, row in top_3_owners.iterrows():
        owner_name = row[owner_col]
        total_patents = row[total_col]
        
        # Get classification columns (skip owner and total)
        class_cols = df.columns[2:]
        
        # Convert row values to numeric and get top 3
        row_values = pd.to_numeric(row[class_cols], errors='coerce').fillna(0)
        top_3_classes = row_values.nlargest(3)
        top_3_classes = top_3_classes[top_3_classes > 0]  # Only non-zero values
        
        # Clean up classification names and create dataframe
        class_data = []
        for class_code, count in top_3_classes.items():
            # Clean up the classification name (take part before colon)
            class_name = class_code.split(':')[0].strip() if ':' in str(class_code) else str(class_code)
            class_data.append({
                'Classification Code': class_name,
                'Patent Count': int(count)
            })
        
        top3_df = pd.DataFrame(class_data)
        results[f"{owner_name} (Total: {int(total_patents)})"] = top3_df
    
    return results


if __name__ == "__main__":
    show_ipc_cpc_classification_tab()