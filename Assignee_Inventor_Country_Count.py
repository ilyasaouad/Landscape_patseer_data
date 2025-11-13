import pandas as pd

"""
Merge, Assignee, Country, Count and Inventor, Country, Count, in files  

Output: Inventors_Country_Count, Assignee_Country_Count.

Some  Country as missing. we have to processed.

"""

def process_country_count_data():
    # File paths
    assignee_count_path = (
        r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\Assignee_Count.csv"
    )
    assignee_country_path = (
        r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\Assignee_Country.csv"
    )

    inventor_count_path = (
        r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\Inventor_Count.csv"
    )
    inventor_country_path = (
        r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\Inventor_Country.csv"
    )

    output_dir = r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data"

    try:
        # Process Assignee data
        df_assignee_count = pd.read_csv(assignee_count_path, encoding="utf-8")
        df_assignee_country = pd.read_csv(assignee_country_path, encoding="utf-8")

        # Merge Assignee_Count with Assignee_Country
        df_assignee_merged = df_assignee_count.merge(
            df_assignee_country[["Assignee", "Country"]], on="Assignee", how="left"
        )

        # Fill missing countries with "None"
        df_assignee_merged["Country"] = df_assignee_merged["Country"].fillna("None")

        # Reorder columns: Country, Assignee, Count
        df_assignee_merged = df_assignee_merged[["Country", "Assignee", "Count"]]

        # Save to CSV
        assignee_country_count_path = f"{output_dir}\\Assignee_Country_Count.csv"
        df_assignee_merged.to_csv(
            assignee_country_count_path, index=False, encoding="utf-8"
        )

        print(f"✅ Assignee_Country_Count.csv created: {assignee_country_count_path}")
        print(f"   Rows: {len(df_assignee_merged)}")
        print(f"\n📊 Assignee data sample:")
        print(df_assignee_merged.head(10))

        # Process Inventor data
        df_inventor_count = pd.read_csv(inventor_count_path, encoding="utf-8")
        df_inventor_country = pd.read_csv(inventor_country_path, encoding="utf-8")

        # Rename "Total" to "Count" for consistency
        df_inventor_count = df_inventor_count.rename(columns={"Total": "Count"})

        # Merge Inventor_Count with Inventor_Country
        df_inventor_merged = df_inventor_count.merge(
            df_inventor_country[["Inventor", "Country"]], on="Inventor", how="left"
        )

        # Remove rows with empty country
        df_inventor_merged = df_inventor_merged[df_inventor_merged["Country"].notna()]
        df_inventor_merged = df_inventor_merged[
            df_inventor_merged["Country"].str.strip() != ""
        ]

        # Reorder columns: Country, Inventor, Count
        df_inventor_merged = df_inventor_merged[["Country", "Inventor", "Count"]]

        # Save to CSV
        inventor_country_count_path = f"{output_dir}\\Inventor_Country_Count.csv"
        df_inventor_merged.to_csv(
            inventor_country_count_path, index=False, encoding="utf-8"
        )

        print(f"\n✅ Inventor_Country_Count.csv created: {inventor_country_count_path}")
        print(f"   Rows: {len(df_inventor_merged)}")
        print(f"\n📊 Inventor data sample:")
        print(df_inventor_merged.head(10))

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
