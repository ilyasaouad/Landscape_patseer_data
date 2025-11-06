import streamlit as st
import pandas as pd
import pycountry
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Patent Analysis Dashboard", layout="wide")

# Create tabs for different analyses
tab1, tab2 = st.tabs(["Geographic Analysis", "Owner & Time Analysis"])

with tab1:
    st.title("Patent Filings by Country")

    # --- Read country dataset ---
    country_csv_path = (
        r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\assignee_country.csv"
    )
    try:
        # Read the CSV file - try different approaches to handle malformed headers
        df = pd.read_csv(country_csv_path, header=0)

        # If the first approach doesn't work, try reading without header and setting it manually
        if df.columns[0] not in ["Assignee Country", "Total"]:
            # Try reading as if no header and set columns
            df = pd.read_csv(
                country_csv_path, header=None, names=["Assignee Country", "Total"]
            )

        # Clean up the data
        # Remove any empty rows
        df = df.dropna()

        # Convert Total column to numeric, handling any string formatting
        df["Total"] = pd.to_numeric(df["Total"], errors="coerce")

        # Remove any rows where conversion failed
        df = df.dropna()

        st.write("Country data loaded successfully!")
        st.dataframe(df, use_container_width=True)

        # Ensure the CSV has the expected columns
        if "Assignee Country" not in df.columns or "Total" not in df.columns:
            st.error(
                "The CSV file must contain 'Assignee Country' and 'Total' columns."
            )
        else:
            # Convert ISO-2 → ISO-3
            def iso2_to_iso3(code):
                try:
                    c = pycountry.countries.get(alpha_2=code.strip())
                    return c.alpha_3 if c else None
                except:
                    return None

            df["iso_alpha3"] = df["Assignee Country"].apply(iso2_to_iso3)

            # Remove rows where ISO-3 conversion failed
            df = df.dropna(subset=["iso_alpha3"])

            # -------------------------------
            # ✅ Global map
            # -------------------------------
            st.subheader(" Global Map – Patent Filings")

            fig_global = px.choropleth(
                df,
                locations="iso_alpha3",
                color="Total",
                hover_name="Assignee Country",
                hover_data={"Total": True},
                color_continuous_scale="OrRd",
                projection="natural earth",
            )

            fig_global.update_layout(
                coloraxis_colorbar=dict(title="Total Patents", ticksuffix=" ")
            )

            st.plotly_chart(fig_global, width="stretch")

            # -------------------------------
            # ✅ Nordic focus (FI, SE, NO, DK, IS)
            # -------------------------------
            st.subheader(" Nordic Region – Patent Filings")

            nordic_codes = ["FI", "SE", "NO", "DK", "IS"]
            df_nordic = df[df["Assignee Country"].isin(nordic_codes)]

            if not df_nordic.empty:
                col1, col2 = st.columns(2)

                with col1:
                    fig_nordic = px.choropleth(
                        df_nordic,
                        locations="iso_alpha3",
                        color="Total",
                        hover_name="Assignee Country",
                        hover_data={"Total": True},
                        color_continuous_scale="Blues",
                        scope="europe",  # zoom on Europe/Nordics
                        projection="natural earth",
                    )

                    fig_nordic.update_layout(
                        coloraxis_colorbar=dict(title="Total Patents", ticksuffix=" ")
                    )

                    st.plotly_chart(fig_nordic, width="stretch")

                with col2:
                    fig_bar = px.bar(
                        df_nordic,
                        x="Assignee Country",
                        y="Total",
                        color="Assignee Country",
                        title="Patent Filings by Nordic Country",
                    )
                    fig_bar.update_layout(showlegend=False)
                    st.plotly_chart(fig_bar, width="stretch")
            else:
                st.write("No Nordic country data found in the dataset.")

    except FileNotFoundError:
        st.error(f"Country CSV file not found at: {country_csv_path}")
        st.write("Please check the file path and make sure the file exists.")
    except Exception as e:
        st.error(f"Error reading the country CSV file: {str(e)}")
        st.write("Please check the CSV file format and content.")

with tab2:
    st.title(" Patent Filings by Owner & Time")

    # --- Read owner-year dataset ---
    owner_csv_path = (
        r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\owner_year_count.csv"
    )
    try:
        df_owner = pd.read_csv(owner_csv_path)

        # Clean the data
        df_owner = df_owner.dropna()
        df_owner["Application Year"] = pd.to_numeric(
            df_owner["Application Year"], errors="coerce"
        )
        df_owner["Count"] = pd.to_numeric(df_owner["Count"], errors="coerce")
        df_owner = df_owner.dropna()

        st.write("Owner-year data loaded successfully!")
        st.dataframe(df_owner, use_container_width=True)

        # Create subtabs for different analyses
        subtab1, subtab2, subtab3, subtab4 = st.tabs(
            [
                "📈 Time Trends",
                "🏆 Top Owners",
                "🔥 Activity Heatmap",
                "📊 Owner Timeline",
            ]
        )

        with subtab1:
            st.subheader("📈 Patent Filings Over Time")

            # Aggregate by year
            yearly_counts = (
                df_owner.groupby("Application Year")["Count"].sum().reset_index()
            )

            fig_time = px.line(
                yearly_counts,
                x="Application Year",
                y="Count",
                title="Total Patent Filings by Year",
                markers=True,
            )
            fig_time.update_layout(
                xaxis_title="Year", yaxis_title="Number of Patents", showlegend=False
            )
            st.plotly_chart(fig_time, use_container_width=True)

            # Show peak years
            peak_year = yearly_counts.loc[yearly_counts["Count"].idxmax()]
            st.info(
                f"📊 Peak year: {int(peak_year['Application Year'])} with {int(peak_year['Count'])} patents"
            )

        with subtab2:
            st.subheader("🏆 Top Patent Owners")

            # Top owners by total patents
            owner_totals = (
                df_owner.groupby("Current Owner")["Count"].sum().reset_index()
            )
            owner_totals = owner_totals.sort_values("Count", ascending=False)

            # Show top 15 owners
            top_owners = owner_totals.head(15)

            col1, col2 = st.columns([2, 1])

            with col1:
                fig_owners = px.bar(
                    top_owners,
                    x="Count",
                    y="Current Owner",
                    orientation="h",
                    title="Top 15 Patent Owners (Total Patents)",
                    color="Count",
                    color_continuous_scale="viridis",
                )
                fig_owners.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig_owners, use_container_width=True)

            with col2:
                st.write("**Top 5 Owners:**")
                for i, row in top_owners.head(5).iterrows():
                    st.metric(row["Current Owner"], f"{int(row['Count'])} patents")

        with subtab3:
            st.subheader("🔥 Owner Activity Heatmap")

            # Create pivot table for heatmap
            pivot_data = df_owner.pivot_table(
                index="Current Owner",
                columns="Application Year",
                values="Count",
                fill_value=0,
            )

            # Show only top 20 owners to keep heatmap readable
            owner_totals = (
                df_owner.groupby("Current Owner")["Count"].sum().reset_index()
            )
            top_owner_names = owner_totals.nlargest(20, "Count")[
                "Current Owner"
            ].tolist()
            pivot_subset = pivot_data.loc[pivot_data.index.isin(top_owner_names)]

            fig_heatmap = px.imshow(
                pivot_subset.values,
                x=pivot_subset.columns,
                y=pivot_subset.index,
                color_continuous_scale="YlOrRd",
                aspect="auto",
                title="Patent Activity Heatmap: Top 20 Owners by Year",
            )
            fig_heatmap.update_layout(
                xaxis_title="Application Year", yaxis_title="Patent Owner", height=600
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

        with subtab4:
            st.subheader("📊 Owner Timeline - Patents by Year per Owner")

            # Get top 10 owners to keep the chart readable
            owner_totals = (
                df_owner.groupby("Current Owner")["Count"].sum().reset_index()
            )
            owner_totals = owner_totals.sort_values("Count", ascending=False)
            top_10_owners = owner_totals.head(10)["Current Owner"].tolist()

            # Filter data for top 10 owners
            df_top_owners = df_owner[df_owner["Current Owner"].isin(top_10_owners)]

            # Create line chart with different lines for each owner
            fig_timeline = px.line(
                df_top_owners,
                x="Application Year",
                y="Count",
                color="Current Owner",
                title="Patent Filings Timeline: Top 10 Owners",
                markers=True,
                line_shape="linear",
            )

            fig_timeline.update_layout(
                xaxis_title="Application Year",
                yaxis_title="Number of Patents",
                height=500,
                legend=dict(
                    orientation="v", yanchor="top", y=1, xanchor="left", x=1.02
                ),
            )

            st.plotly_chart(fig_timeline, use_container_width=True)

            # Add some insights about the timeline
            st.write("**Key Observations:**")
            col1, col2 = st.columns(2)

            with col1:
                # Find which owner had the most patents in a single year
                peak_owner_year = df_top_owners.loc[df_top_owners["Count"].idxmax()]
                st.info(
                    f"🏆 Peak performance: {peak_owner_year['Current Owner'][:30]} in {int(peak_owner_year['Application Year'])} with {int(peak_owner_year['Count'])} patents"
                )

            with col2:
                # Show owner activity span
                owner_spans = (
                    df_top_owners.groupby("Current Owner")["Application Year"]
                    .agg(["min", "max"])
                    .reset_index()
                )
                owner_spans["span"] = owner_spans["max"] - owner_spans["min"]
                most_consistent = owner_spans.loc[owner_spans["span"].idxmax()]
                st.info(
                    f"🔄 Most consistent: {most_consistent['Current Owner'][:30]} ({int(most_consistent['span'])} year span)"
                )

            # Show which owners are selected
            st.write("**Top 10 Owners included in this chart:**")
            for i, owner in enumerate(top_10_owners, 1):
                owner_total = owner_totals[owner_totals["Current Owner"] == owner][
                    "Count"
                ].iloc[0]
                st.write(f"{i}. {owner} ({int(owner_total)} total patents)")

            # Additional insights
            st.subheader("📊 Key Insights")

            col1, col2, col3 = st.columns(3)

            with col1:
                # Most active year overall
                most_active_year = yearly_counts.loc[yearly_counts["Count"].idxmax()]
                st.metric(
                    "Most Active Year",
                    f"{int(most_active_year['Application Year'])}",
                    f"{int(most_active_year['Count'])} patents",
                )

            with col2:
                # Most active owner
                most_active_owner = owner_totals.iloc[0]
                st.metric(
                    "Top Owner",
                    (
                        most_active_owner["Current Owner"][:20] + "..."
                        if len(most_active_owner["Current Owner"]) > 20
                        else most_active_owner["Current Owner"]
                    ),
                    f"{int(most_active_owner['Count'])} patents",
                )

            with col3:
                # Number of unique owners
                total_owners = df_owner["Current Owner"].nunique()
                st.metric("Total Owners", f"{total_owners}")

            # Show year range
            year_range = f"{int(df_owner['Application Year'].min())} - {int(df_owner['Application Year'].max())}"
            st.info(f"📅 Data covers: {year_range}")

    except FileNotFoundError:
        st.error(f"Owner-year CSV file not found at: {owner_csv_path}")
        st.write("Please check the file path and make sure the file exists.")
    except Exception as e:
        st.error(f"Error reading the owner-year CSV file: {str(e)}")
        st.write("Please check the CSV file format and content.")
