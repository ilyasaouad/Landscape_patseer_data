import streamlit as st
import pandas as pd
import pycountry
import plotly.express as px
import plotly.graph_objects as go


def show_all_family_country_tab():
    st.title("Patent Filings by All Family Country")

    # --- Read all family country dataset ---
    family_csv_path = r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\All_family_Country_Map.csv"
    try:
        df_family = pd.read_csv(family_csv_path)

        # Clean the data
        df_family = df_family.dropna()
        df_family["Total"] = pd.to_numeric(df_family["Total"], errors="coerce")
        df_family = df_family.dropna()

        st.write("Family country data loaded successfully!")
        st.dataframe(df_family, width="stretch")

        # Separate standard country codes from non-standard ones
        def iso2_to_iso3(code):
            try:
                c = pycountry.countries.get(alpha_2=code.strip())
                return c.alpha_3 if c else None
            except:
                return None

        df_family["iso_alpha3"] = df_family["All Family Country"].apply(iso2_to_iso3)

        # Split data: valid ISO codes for map, all codes for bar chart
        df_family_map = df_family[df_family["iso_alpha3"].notna()]
        df_family_all = df_family.copy()

        # Store non-standard codes for legend
        non_standard = df_family[df_family["iso_alpha3"].isna()]

        # -------------------------------
        # ✅ World map
        # -------------------------------
        st.markdown(
            "<h2 style='color: #00BFFF;'>Global Map – Patent Family Filings</h2>",
            unsafe_allow_html=True,
        )

        fig_world = px.choropleth(
            df_family_map,
            locations="iso_alpha3",
            color="Total",
            hover_name="All Family Country",
            hover_data={"Total": True},
            color_continuous_scale="OrRd",
            projection="natural earth",
        )

        fig_world.update_layout(
            coloraxis_colorbar=dict(title="Total Patents", ticksuffix=" "),
            height=600,
            title_font_color="#00BFFF",
        )

        # Add annotation for non-standard codes as legend
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

        st.plotly_chart(fig_world, width="stretch")

        # -------------------------------
        # ✅ Bar chart (horizontal, descending)
        # -------------------------------
        st.subheader("📊 Patent Family Filings by Country")

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

        st.plotly_chart(fig_bar, width="stretch")

        # -------------------------------
        # ✅ Nordic Data Section
        # -------------------------------
        st.subheader("Nordic Data – Patent Family Filings")

        nordic_codes = ["FI", "SE", "NO", "DK", "IS"]
        df_nordic = df_family[df_family["All Family Country"].isin(nordic_codes)].copy()

        # Add missing Nordic countries with 0 total
        existing_nordic = df_nordic["All Family Country"].tolist()
        missing_nordic = [code for code in nordic_codes if code not in existing_nordic]

        if missing_nordic:
            for code in missing_nordic:
                new_row = pd.DataFrame(
                    {
                        "All Family Country": [code],
                        "Total": [0],
                        "iso_alpha3": [
                            (
                                pycountry.countries.get(alpha_2=code).alpha_3
                                if pycountry.countries.get(alpha_2=code)
                                else None
                            )
                        ],
                    }
                )
                df_nordic = pd.concat([df_nordic, new_row], ignore_index=True)

        if not df_nordic.empty:
            # Display Nordic dataframe
            st.write("**Nordic Countries Data:**")
            st.dataframe(df_nordic[["All Family Country", "Total"]], width="stretch")

            # Nordic map
            st.subheader("🗺️ Nordic Map – Patent Family Filings")

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

            st.plotly_chart(fig_nordic, width="stretch")

            # Nordic bar chart
            st.subheader("📊 Patent Family Filings by Nordic Country")

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

            st.plotly_chart(fig_nordic_bar, width="stretch")
        else:
            st.write("No Nordic country data found in the dataset.")

    except FileNotFoundError:
        st.error(f"Family country CSV file not found at: {family_csv_path}")
        st.write("Please check the file path and make sure the file exists.")
    except Exception as e:
        st.error(f"Error reading the family country CSV file: {str(e)}")
        st.write("Please check the CSV file format and content.")
