import streamlit as st
import pandas as pd
import pycountry
import plotly.express as px

from utils.file_paths import raw
from utils.constants import NORDIC_COUNTRY_CODES


def iso2_to_iso3(code):
    """Convert ISO 2-letter country code to ISO 3-letter code."""
    try:
        country = pycountry.countries.get(alpha_2=code.strip())
        return country.alpha_3 if country else None
    except (AttributeError, KeyError):
        return None


def show_all_family_country_tab():
    st.title("Geographic Patent Analysis")
    
    # Add explanatory comment
    st.markdown("""
    **Understanding Priority vs Family Countries:**  
    The priority country table shows where each invention was first filed. The patent family table shows where the same inventions were later filed internationally. The priority filing itself is not counted again in the family table.
    
    That is why some countries have many priority filings but fewer family filings - most applications start in the priority country, but they are not filed again in that same country when the applicant expands internationally.
    
    **Example:** Finland (FI) has many priority filings because many inventions originate there, but FI appears less often in the family table since an invention that starts in FI is usually filed later in EP, US, or WO, and not again in FI. As a result, FI ranks high in the Priority Countries tab but low in the family table (see Priority Countries tab).
    """)
    
    # Create two tabs for different analyses
    tab1, tab2 = st.tabs(["📍 Patent Families", "🌍 Priority Countries"])
    
    with tab1:
        show_patent_families_analysis()
    
    with tab2:
        show_priority_countries_analysis()


def show_patent_families_analysis():
    st.subheader("Patent Families Analysis")

    # Try both possible filenames
    possible_files = [
        "All_family_Country_Map.csv",
        "All_Family_Country_Map.csv"
    ]
    
    df_family = None
    file_path = None
    
    for filename in possible_files:
        try:
            file_path = raw(filename)
            df_family = pd.read_csv(file_path)
            break
        except FileNotFoundError:
            continue
        except Exception as e:
            continue
    
    if df_family is None:
        st.error("Family country CSV file not found. Checked files: " + str(possible_files))
        return

    try:

        df_family = df_family.dropna()
        df_family["Total"] = pd.to_numeric(df_family["Total"], errors="coerce")
        df_family = df_family.dropna()

        st.write("Family country data loaded successfully!")
        st.dataframe(df_family, use_container_width=True)

        df_family["iso_alpha3"] = df_family["All Family Country"].apply(iso2_to_iso3)

        df_family_map = df_family[df_family["iso_alpha3"].notna()]
        df_family_all = df_family.copy()
        non_standard = df_family[df_family["iso_alpha3"].isna()]

        st.markdown("## Global Map – Patent Family Filings")

        fig_world = px.choropleth(
            df_family_map,
            locations="iso_alpha3",
            color="Total",
            hover_name="All Family Country",
            hover_data={"Total": True},
            color_continuous_scale="OrRd",
            projection="natural earth",
        )

        if not non_standard.empty:
            legend_text = "Non-standard codes:<br>"
            for _, row in non_standard.iterrows():
                legend_text += f"{row['All Family Country']}: {int(row['Total'])}<br>"

            fig_world.add_annotation(
                text=legend_text,
                xref="paper",
                yref="paper",
                x=0,
                y=0,
                showarrow=False,
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="black",
                borderwidth=1,
                font=dict(size=10),
                align="left",
                xanchor="left",
                yanchor="bottom",
            )

        st.plotly_chart(fig_world, use_container_width=True)

        st.subheader("Patent Family Filings by Country")

        df_sorted = df_family_all.sort_values("Total", ascending=True)

        fig_bar = px.bar(
            df_sorted,
            x="Total",
            y="All Family Country",
            orientation="h",
            title="Patent Family Filings by Country (All Codes)",
            color="Total",
            color_continuous_scale="Viridis",
        )

        fig_bar.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("Nordic Data – Patent Family Filings")

        df_nordic = df_family[
            df_family["All Family Country"].isin(NORDIC_COUNTRY_CODES)
        ].copy()

        existing = df_nordic["All Family Country"].tolist()
        missing = [code for code in NORDIC_COUNTRY_CODES if code not in existing]

        for code in missing:
            iso3_code = iso2_to_iso3(code)
            df_nordic = pd.concat(
                [
                    df_nordic,
                    pd.DataFrame(
                        {
                            "All Family Country": [code],
                            "Total": [0],
                            "iso_alpha3": [iso3_code],
                        }
                    ),
                ],
                ignore_index=True,
            )

        st.write("**Nordic Countries Data:**")
        st.dataframe(
            df_nordic[["All Family Country", "Total"]], use_container_width=True
        )

        st.subheader("Nordic Map – Patent Family Filings")

        fig_nordic = px.choropleth(
            df_nordic,
            locations="iso_alpha3",
            color="Total",
            hover_name="All Family Country",
            hover_data={"Total": True},
            color_continuous_scale="OrRd",
            scope="europe",
            projection="natural earth",
        )

        fig_nordic.update_layout(
            coloraxis_colorbar=dict(title="Total Patents", ticksuffix=" "),
            height=600,
        )

        st.plotly_chart(fig_nordic, use_container_width=True)

        st.subheader("Patent Family Filings by Nordic Country")

        df_nordic_sorted = df_nordic.sort_values("Total", ascending=True)

        fig_nordic_bar = px.bar(
            df_nordic_sorted,
            x="Total",
            y="All Family Country",
            orientation="h",
            title="Patent Family Filings by Nordic Country",
            color="Total",
            color_continuous_scale="Blues",
        )

        fig_nordic_bar.update_layout(
            yaxis={"categoryorder": "total ascending"}, height=400
        )

        st.plotly_chart(fig_nordic_bar, use_container_width=True)

    except FileNotFoundError:
        st.error(f"Family country CSV file not found at: {file_path}")
    except Exception as e:
        st.error(f"Error reading the family country CSV file: {str(e)}")


def show_priority_countries_analysis():
    st.subheader("Priority Countries Analysis")

    # Try both possible filenames
    possible_files = [
        "Priority_Country_Map.csv",
        "Priority_country_Map.csv"
    ]
    
    df_priority = None
    file_path = None
    
    for filename in possible_files:
        try:
            file_path = raw(filename)
            df_priority = pd.read_csv(file_path)
            break
        except FileNotFoundError:
            continue
        except Exception as e:
            continue
    
    if df_priority is None:
        st.error("Priority country CSV file not found. Checked files: " + str(possible_files))
        return

    try:

        df_priority = df_priority.dropna()
        df_priority["Total"] = pd.to_numeric(df_priority["Total"], errors="coerce")
        df_priority = df_priority.dropna()

        st.write("Priority country data loaded successfully!")
        st.dataframe(df_priority, use_container_width=True)

        df_priority["iso_alpha3"] = df_priority["Priority Country"].apply(iso2_to_iso3)

        df_priority_map = df_priority[df_priority["iso_alpha3"].notna()]
        df_priority_all = df_priority.copy()
        non_standard = df_priority[df_priority["iso_alpha3"].isna()]

        st.markdown("## Global Map – Priority Countries")

        fig_world = px.choropleth(
            df_priority_map,
            locations="iso_alpha3",
            color="Total",
            hover_name="Priority Country",
            hover_data={"Total": True},
            color_continuous_scale="Purples",
            projection="natural earth",
        )

        if not non_standard.empty:
            legend_text = "Non-standard codes:<br>"
            for _, row in non_standard.iterrows():
                legend_text += f"{row['Priority Country']}: {int(row['Total'])}<br>"

            fig_world.add_annotation(
                text=legend_text,
                xref="paper",
                yref="paper",
                x=0,
                y=0,
                showarrow=False,
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="black",
                borderwidth=1,
                font=dict(size=10),
                align="left",
                xanchor="left",
                yanchor="bottom",
            )

        st.plotly_chart(fig_world, use_container_width=True)

        st.subheader("Priority Filings by Country")

        df_sorted = df_priority_all.sort_values("Total", ascending=True)

        fig_bar = px.bar(
            df_sorted,
            x="Total",
            y="Priority Country",
            orientation="h",
            title="Priority Filings by Country (All Codes)",
            color="Total",
            color_continuous_scale="Plasma",
        )

        fig_bar.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("Nordic Data – Priority Countries")

        df_nordic = df_priority[
            df_priority["Priority Country"].isin(NORDIC_COUNTRY_CODES)
        ].copy()

        existing = df_nordic["Priority Country"].tolist()
        missing = [code for code in NORDIC_COUNTRY_CODES if code not in existing]

        for code in missing:
            iso3_code = iso2_to_iso3(code)
            df_nordic = pd.concat(
                [
                    df_nordic,
                    pd.DataFrame(
                        {
                            "Priority Country": [code],
                            "Total": [0],
                            "iso_alpha3": [iso3_code],
                        }
                    ),
                ],
                ignore_index=True,
            )

        st.write("**Nordic Countries Data:**")
        st.dataframe(
            df_nordic[["Priority Country", "Total"]], use_container_width=True
        )

        st.subheader("Nordic Map – Priority Countries")

        fig_nordic = px.choropleth(
            df_nordic,
            locations="iso_alpha3",
            color="Total",
            hover_name="Priority Country",
            hover_data={"Total": True},
            color_continuous_scale="Purples",
            scope="europe",
            projection="natural earth",
        )

        fig_nordic.update_layout(
            coloraxis_colorbar=dict(title="Total Patents", ticksuffix=" "),
            height=600,
        )

        st.plotly_chart(fig_nordic, use_container_width=True)

        st.subheader("Priority Filings by Nordic Country")

        df_nordic_sorted = df_nordic.sort_values("Total", ascending=True)

        fig_nordic_bar = px.bar(
            df_nordic_sorted,
            x="Total",
            y="Priority Country",
            orientation="h",
            title="Priority Filings by Nordic Country",
            color="Total",
            color_continuous_scale="Greens",
        )

        fig_nordic_bar.update_layout(
            yaxis={"categoryorder": "total ascending"}, height=400
        )

        st.plotly_chart(fig_nordic_bar, use_container_width=True)

    except FileNotFoundError:
        st.error(f"Priority country CSV file not found at: {file_path}")
    except Exception as e:
        st.error(f"Error reading the priority country CSV file: {str(e)}")
