#!/usr/bin/env python3
"""
IPC and CPC Classification Analysis
Analyzes patent classification data for current owners.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_paths import raw


def show_ipc_cpc_classification_tab():
    """
    Streamlit UI for IPC and CPC Classification Analysis.
    Shows top 15 current owners with their top 3 classification codes.
    """
    
    st.title("IPC and CPC Classification Analysis")
    
    # Load and process IPC data
    st.markdown("## IPC (International Patent Classification) Analysis")
    ipc_summary = create_classification_summary("Current-Owner_IPC-Full.csv", "IPC")
    
    if ipc_summary is not None:
        st.markdown("### Top 15 Current Owners - Top 5 IPC Classifications")
        
        # Display classification descriptions
        display_class_descriptions(ipc_summary, "IPC")
        
        st.dataframe(ipc_summary, use_container_width=True)
    
    # Load and process CPC data
    st.markdown("## CPC (Cooperative Patent Classification) Analysis") 
    cpc_summary = create_classification_summary("Current-Owner_CPC-Full.csv", "CPC")
    
    if cpc_summary is not None:
        st.markdown("### Top 15 Current Owners - Top 5 CPC Classifications")
        
        # Display classification descriptions
        display_class_descriptions(cpc_summary, "CPC")
        
        st.dataframe(cpc_summary, use_container_width=True)


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