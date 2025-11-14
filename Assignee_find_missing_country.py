import pandas as pd
import re


def find_missing_country_records():
    # File paths
    assignee_country_count_path = r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\Assignee_Country_Count.csv"

    assignee_country_path = (
        r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\Assignee_Country.csv"
    )

    assignee_inventor_xlsx_path = r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\Assignee_Inventor_Country.xlsx"

    output_dir = r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data"

    try:
        # Read files
        df_assignee_count = pd.read_csv(assignee_country_count_path, encoding="utf-8")
        df_assignee_country = pd.read_csv(assignee_country_path, encoding="utf-8")
        df_excel = pd.read_excel(assignee_inventor_xlsx_path)

        print("Step 1: Finding countries for assignees with None...")

        # Get assignees with None country (top 15 by count)
        df_none_assignees = df_assignee_count[
            df_assignee_count["Country"].isna()
        ].nlargest(15, "Count")
        none_assignees_list = df_none_assignees["Assignee"].tolist()

        print(f"Assignees with missing country: {len(none_assignees_list)}")
        print(none_assignees_list)

        # Function to extract country code
        def extract_country(text):
            match = re.search(r"\(\s*([A-Z]{2})\s*\)", str(text))
            return match.group(1) if match else None

        # Function to extract name
        def extract_name(text):
            text = str(text)
            if "(" in text:
                return text[: text.rfind("(")].strip()
            return text.strip()

        # Search for countries in Excel file
        found_countries = {}
        for assignee in none_assignees_list:
            # Search in Current Assignee column
            matches_assignee = df_excel[
                df_excel["Current Assignee"].str.contains(
                    assignee, case=False, na=False
                )
            ]
            # Search in Current Owner column
            matches_owner = df_excel[
                df_excel["Current Owner"].str.contains(assignee, case=False, na=False)
            ]

            # Combine matches
            matches = pd.concat([matches_assignee, matches_owner]).drop_duplicates()

            # Find country code in any matching record
            for _, record in matches.iterrows():
                # Check Current Assignee for country
                country = extract_country(record["Current Assignee"])
                if country:
                    found_countries[assignee] = country
                    print(f"✅ Found country for {assignee}: {country}")
                    break

                # Check Current Owner for country
                country = extract_country(record["Current Owner"])
                if country:
                    found_countries[assignee] = country
                    print(f"✅ Found country for {assignee}: {country}")
                    break

        # Update Assignee_Country.csv with found countries
        print(
            f"\nStep 2: Updating Assignee_Country.csv with {len(found_countries)} new entries..."
        )

        for assignee, country in found_countries.items():
            if country:
                new_row = pd.DataFrame({"Assignee": [assignee], "Country": [country]})
                df_assignee_country = pd.concat(
                    [df_assignee_country, new_row], ignore_index=True
                )

        # Remove duplicates, keep first
        df_assignee_country = df_assignee_country.drop_duplicates(
            subset=["Assignee"], keep="first"
        )

        # Save updated file
        df_assignee_country.to_csv(assignee_country_path, index=False, encoding="utf-8")
        print(f"✅ Updated Assignee_Country.csv")

        # Re-merge with Assignee_Count to update counts
        print(f"\nStep 3: Updating Assignee_Country_Count.csv...")

        df_assignee_merged = df_assignee_count.merge(
            df_assignee_country[["Assignee", "Country"]],
            on="Assignee",
            how="left",
            suffixes=("_count", "_country"),
        )

        # Use Country_country column (from updated Assignee_Country)
        if "Country_country" in df_assignee_merged.columns:
            df_assignee_merged["Country"] = df_assignee_merged["Country_country"]
        elif "Country_count" in df_assignee_merged.columns:
            df_assignee_merged["Country"] = df_assignee_merged["Country_count"]

        df_assignee_merged["Country"] = df_assignee_merged["Country"].fillna("None")
        df_assignee_merged = df_assignee_merged[["Country", "Assignee", "Count"]]

        assignee_country_count_path_updated = (
            f"{output_dir}\\Assignee_Country_Count.csv"
        )
        df_assignee_merged.to_csv(
            assignee_country_count_path_updated, index=False, encoding="utf-8"
        )
        print(f"✅ Updated Assignee_Country_Count.csv")

        # Find remaining None assignees
        print(f"\nStep 4: Finding Record Numbers for remaining None assignees...")

        df_none_assignees_remaining = df_assignee_merged[
            df_assignee_merged["Country"] == "None"
        ].nlargest(15, "Count")
        remaining_assignees = df_none_assignees_remaining["Assignee"].tolist()

        print(f"\nRemaining assignees with None country:")
        print(df_none_assignees_remaining[["Assignee", "Country", "Count"]])

        # Find Record Numbers for remaining None assignees
        records_list = []
        for assignee in remaining_assignees:
            matching_records = df_excel[
                df_excel["Current Owner"].str.contains(assignee, case=False, na=False)
            ]

            if not matching_records.empty:
                for _, record in matching_records.iterrows():
                    records_list.append(
                        {
                            "Record Number": record["Record Number"],
                            "Assignee": assignee,
                            "Current Owner": record["Current Owner"],
                        }
                    )

        df_missing = pd.DataFrame(records_list)
        # Keep only first record for each Assignee
        df_missing = df_missing.drop_duplicates(subset=["Assignee"], keep="first")
        df_missing = df_missing[["Record Number", "Assignee", "Current Owner"]]

        output_path = f"{output_dir}\\Assignee_Missing_Country.csv"
        df_missing.to_csv(output_path, index=False, encoding="utf-8")

        print(f"\n✅ Assignee_Missing_Country.csv created: {output_path}")
        print(f"   Rows: {len(df_missing)}")
        print(f"\n📊 Sample data:")
        print(df_missing.head(10))

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    find_missing_country_records()
