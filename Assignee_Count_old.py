import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


"""
Using Assignee_Count.csv from patseer data

Using: Assignee_Country.csv from patseer data


"""


def show_assignee_count_tab():
    st.title("Patent Filings by Assignee")

    # --- Read assignee count dataset ---
    assignee_csv_path = (
        r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\Assignee_Count.csv"
    )
    assignee_country_csv_path = (
        r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\Assignee_Country.csv"
    )

    try:
        df_assignee = pd.read_csv(assignee_csv_path, encoding="utf-8")
        df_assignee_country = pd.read_csv(assignee_country_csv_path, encoding="utf-8")

        # Clean the data
        df_assignee = df_assignee.dropna()
        df_assignee["Count"] = pd.to_numeric(df_assignee["Count"], errors="coerce")
        df_assignee = df_assignee.dropna()

        # Check if assignee_country data exists
        if not df_assignee_country.empty:
            # Get unique assignee-country mapping (take first match)
            df_country_map = df_assignee_country.drop_duplicates(
                subset=["Assignee"], keep="first"
            )

            # Merge to add country column
            df_assignee = df_assignee.merge(
                df_country_map[["Assignee", "Country"]], on="Assignee", how="left"
            )

            # Reorder columns: Country first, then Assignee, then Count
            df_assignee = df_assignee[["Country", "Assignee", "Count"]]
        else:
            st.warning(
                "⚠️ Assignee_Country.csv is empty. Showing Assignee and Count only."
            )

        # Display dataframe with country prefix
        if "Country" in df_assignee.columns:
            df_assignee_display = df_assignee.copy()
            df_assignee_display["Assignee"] = (
                df_assignee_display["Country"].fillna("")
                + " - "
                + df_assignee_display["Assignee"]
            )
            df_assignee_display = df_assignee_display[["Assignee", "Count"]]
            st.write("Assignee count data loaded successfully!")
            st.dataframe(df_assignee_display, width="stretch")
        else:
            st.write("Assignee count data loaded successfully!")
            st.dataframe(df_assignee, width="stretch")

        # Get top 15 assignees
        df_top_15 = df_assignee.nlargest(15, "Count")

        # Sort for horizontal bar chart (ascending for better visualization)
        df_top_15_sorted = df_top_15.sort_values("Count", ascending=True)

        # Add country prefix to assignee name
        if "Country" in df_top_15_sorted.columns:
            df_top_15_sorted = df_top_15_sorted.copy()
            df_top_15_sorted["Assignee_Label"] = (
                df_top_15_sorted["Country"].fillna("")
                + " - "
                + df_top_15_sorted["Assignee"]
            )
        else:
            df_top_15_sorted["Assignee_Label"] = df_top_15_sorted["Assignee"]

        # -------------------------------
        # ✅ Horizontal bar chart
        # -------------------------------
        st.markdown(
            "<h2 style='color: #00BFFF;'>Top 15 Patent Assignees</h2>",
            unsafe_allow_html=True,
        )

        fig_bar = px.bar(
            df_top_15_sorted,
            x="Count",
            y="Assignee_Label",
            orientation="h",
            title="Top 15 Patent Assignees by Count",
            color="Count",
            color_continuous_scale="OrRd",
        )

        fig_bar.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)

        st.plotly_chart(fig_bar, width="stretch")

    except FileNotFoundError:
        st.error(f"Assignee count CSV file not found at: {assignee_csv_path}")
        st.write("Please check the file path and make sure the file exists.")
    except Exception as e:
        st.error(f"Error reading the assignee count CSV file: {str(e)}")
        st.write("Please check the CSV file format and content.")
