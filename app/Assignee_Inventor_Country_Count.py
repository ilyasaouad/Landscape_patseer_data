import pandas as pd
import subprocess
import streamlit as st
import plotly.express as px

from utils.file_paths import raw, processed, BASE_DIR

"""
Process Assignee + Inventor country data.

Outputs written to data/processed/:
  ✔ Assignee_Country_Count.csv
  ✔ Inventor_Country_Count.csv
  ✔ Assignee_Country_Count_Updated.csv  (after LLM correction)
"""


# ======================================================================
# 1. PROCESS DATA (runs automatically at Streamlit startup)
# ======================================================================
def process_country_count_data():
    # --------------------------------------------
    # RAW INPUT FILES (from Patseer)
    # --------------------------------------------
    assignee_count_path = raw("Assignee_Count.csv")
    assignee_country_path = raw("Assignee_Country.csv")

    inventor_count_path = raw("Inventor_Count.csv")
    inventor_country_path = raw("Inventor_Country.csv")

    # --------------------------------------------
    # OUTPUT FILES
    # --------------------------------------------
    assignee_output_raw = processed("Assignee_Country_Count.csv")
    inventor_output_raw = processed("Inventor_Country_Count.csv")
    assignee_output_final = processed("Assignee_Country_Count_Updated.csv")

    # --------------------------------------------
    # Path to LLM correction script
    # --------------------------------------------
    llm_script = BASE_DIR / "llm" / "Assignee_find_missing_country_llm.py"

    try:
        # ==========================================================
        # ASSIGNEE PROCESSING
        # ==========================================================
        print("\n📄 Loading Assignee CSV files...")
        df_assignee_count = pd.read_csv(assignee_count_path, encoding="utf-8")
        df_assignee_country = pd.read_csv(assignee_country_path, encoding="utf-8")

        print("🔄 Merging Assignee Count + Country...")
        df_assignee = df_assignee_count.merge(
            df_assignee_country[["Assignee", "Country"]], on="Assignee", how="left"
        )

        df_assignee["Country"] = df_assignee["Country"].fillna("None")
        df_assignee = df_assignee[["Country", "Assignee", "Count"]]

        print("💾 Saving: Assignee_Country_Count.csv")
        assignee_output_raw.parent.mkdir(parents=True, exist_ok=True)
        df_assignee.to_csv(assignee_output_raw, index=False, encoding="utf-8")

        # ==========================================================
        # INVENTOR PROCESSING
        # ==========================================================
        print("\n📄 Loading Inventor CSV files...")
        df_inventor_count = pd.read_csv(inventor_count_path, encoding="utf-8")
        df_inventor_country = pd.read_csv(inventor_country_path, encoding="utf-8")

        # Patseer sometimes uses "Total" instead of "Count"
        if "Total" in df_inventor_count.columns:
            df_inventor_count = df_inventor_count.rename(columns={"Total": "Count"})

        print("🔄 Merging Inventor Count + Country...")
        # Fix: Remove duplicates from country data before merging
        df_inventor_country_clean = df_inventor_country.drop_duplicates(subset=['Inventor'], keep='first')
        df_inventor = df_inventor_count.merge(
            df_inventor_country_clean[["Inventor", "Country"]], on="Inventor", how="left"
        )

        # Remove missing countries (LLM not applied to inventors)
        df_inventor = df_inventor[df_inventor["Country"].notna()]
        df_inventor = df_inventor[df_inventor["Country"].str.strip() != ""]
        df_inventor = df_inventor[["Country", "Inventor", "Count"]]

        print("💾 Saving: Inventor_Country_Count.csv")
        inventor_output_raw.parent.mkdir(parents=True, exist_ok=True)
        df_inventor.to_csv(inventor_output_raw, index=False, encoding="utf-8")

        # ==========================================================
        # CALL LLM TO CORRECT ASSIGNEE COUNTRY
        # ==========================================================
        print("\n🤖 Calling LLM script for Assignee country correction...")
        subprocess.run(["python", str(llm_script)], check=True)

        if assignee_output_final.exists():
            print(f"\n🎉 Updated Assignee File Created:\n   {assignee_output_final}")
        else:
            print("\n⚠ LLM script ran, but updated file NOT found!")

    except Exception as e:
        print(f"\n❌ ERROR in processing: {e}")


# ======================================================================
# 2. STREAMLIT UI – ASSIGNEE ANALYSIS PAGE
# ======================================================================
def show_assignee_inventor_country_count_tab():
    """
    Streamlit UI for Assignee Analysis.
    Loads and displays the LLM-corrected dataset.
    """

    st.title("Assignee Analysis")

    file_path = processed("Assignee_Country_Count_Updated.csv")

    try:
        df = pd.read_csv(file_path, encoding="utf-8")

        st.markdown("### Top 15 Assignees/Applicants and Country of Origin by Patent Count")
        st.markdown("*This analysis shows the leading patent assignees and their countries of origin, providing insights into global innovation leadership and patent filing strategies.*")
        st.dataframe(df, use_container_width=True)

        # Validate required columns
        if "Count" not in df.columns:
            st.error("Column 'Count' missing from dataset.")
            st.write("Columns found:", df.columns.tolist())
            return

        # --------------------------------------------------------------
        # 🔝 TOP 15 ASSIGNEES
        # --------------------------------------------------------------
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
            title="Top 15 Assignees",
            color_continuous_scale="OrRd",
        )

        fig.update_layout(
            height=500,
            xaxis_title="Patent Count",
            yaxis_title="Assignee",
            yaxis={"categoryorder": "total ascending"},
        )

        st.plotly_chart(fig, use_container_width=True)

    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
    except Exception as e:
        st.error(f"Error loading assignee dataset: {e}")


def show_inventor_analysis_tab():
    """
    Streamlit UI for Inventor Analysis.
    Loads and displays the clean inventor dataset.
    """
    
    st.title("Inventor Analysis")

    file_path = processed("Inventor_Country_Count.csv")

    try:
        df = pd.read_csv(file_path, encoding="utf-8")

        st.markdown("### Top Inventors and Country of Origin by Patent Count")
        st.markdown("*This analysis identifies the most prolific inventors and their countries of origin, showcasing individual innovation contributions to the patent landscape.*")
        st.dataframe(df, use_container_width=True)

        # Validate required columns
        if "Count" not in df.columns:
            st.error("Column 'Count' missing from dataset.")
            st.write("Columns found:", df.columns.tolist())
            return

        # --------------------------------------------------------------
        # 🔝 TOP INVENTORS
        # --------------------------------------------------------------
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

    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
    except Exception as e:
        st.error(f"Error loading inventor dataset: {e}")


def show_entity_analysis_tab():
    """
    Streamlit UI for Entity Analysis.
    Contains tabs for both Assignees and Inventors.
    """
    st.title("Entity Analysis")
    
    # Create two tabs for different entity analyses
    tab1, tab2 = st.tabs(["Assignees", "Inventors"])
    
    with tab1:
        show_assignee_inventor_country_count_tab()
    
    with tab2:
        show_inventor_analysis_tab()


def show_assignee_analysis_tab():
    import streamlit as st
    import pandas as pd
    from utils.file_paths import processed

    st.title("Assignee Country Analysis")

    # Load the UPDATED file produced by the LLM
    updated_path = processed("Assignee_Country_Count_Updated.csv")

    try:
        df = pd.read_csv(updated_path, encoding="utf-8")
    except FileNotFoundError:
        st.error(
            "Updated assignee file not found. Please run processing or refresh data."
        )
        return

    st.subheader("Assignee Country Data (Updated)")
    st.dataframe(df, use_container_width=True)

    # Optional: simple charts later
    st.info("Charts can be added here if you want visual analysis.")


# ======================================================================
# 3. Allow standalone execution for testing
# ======================================================================
if __name__ == "__main__":
    process_country_count_data()
