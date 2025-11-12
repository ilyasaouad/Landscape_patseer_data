import pandas as pd
import re


def process_data():
    # Read the dataset
    input_excel_path = r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\Assignee_Inventor_Country.xlsx"
    assignee_count_path = (
        r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\Assignee_Count.csv"
    )
    output_dir = r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data"

    try:
        df = pd.read_excel(input_excel_path)

        # Read Assignee_Count.csv to get lookup table
        df_assignee_count = pd.read_csv(assignee_count_path, encoding="utf-8")
        assignee_lookup = set(df_assignee_count["Assignee"].str.strip().tolist())

        # Extract country code from text (e.g., "NAME ( FI )" -> "FI")
        def extract_country(text):
            match = re.search(r"\(\s*([A-Z]{2})\s*\)", str(text))
            return match.group(1) if match else None

        # Extract name by stripping everything from last '(' onwards
        def extract_name(text):
            text = str(text)
            if "(" in text:
                return text[: text.rfind("(")].strip()
            return text.strip()

        # Process Inventors
        inventors_list = []
        for _, row in df.iterrows():
            inventors_text = row["Inventors"]
            if pd.notna(inventors_text):
                # Split by semicolon
                inventor_entries = [x.strip() for x in str(inventors_text).split(";")]
                for entry in inventor_entries:
                    if entry:
                        name = extract_name(entry)
                        country = extract_country(entry)
                        if name and country:
                            inventors_list.append(
                                {"Inventor": name, "Country": country}
                            )

        df_inventors = pd.DataFrame(inventors_list)

        # Process Assignees
        assignees_list = []
        for _, row in df.iterrows():
            assignee_text = row["Current Assignee"]
            if pd.notna(assignee_text):
                # Split by semicolon (in case multiple assignees)
                assignee_entries = [x.strip() for x in str(assignee_text).split(";")]
                for entry in assignee_entries:
                    if entry:
                        name = extract_name(entry)
                        country = extract_country(entry)
                        # Only keep if name exists in Assignee_Count.csv
                        if name in assignee_lookup and country:
                            assignees_list.append(
                                {"Assignee": name, "Country": country}
                            )

        df_assignees = pd.DataFrame(assignees_list)

        # Remove duplicates - keep only first occurrence of each assignee
        df_assignees = df_assignees.drop_duplicates(subset=["Assignee"], keep="first")

        # Remove duplicates - keep only first occurrence of each assignee
        df_assignees = df_assignees.drop_duplicates(subset=["Assignee"], keep="first")

        # Remove rows with missing country
        df_assignees = df_assignees.dropna(subset=["Country"])

        # Save to CSV files
        inventors_output_path = f"{output_dir}\\Inventor_Country.csv"
        assignees_output_path = f"{output_dir}\\Assignee_Country.csv"

        df_inventors.to_csv(inventors_output_path, index=False)
        df_assignees.to_csv(assignees_output_path, index=False)

        print(f"✅ Data processing completed!")
        print(f"   Inventor_Country.csv: {len(df_inventors)} rows")
        print(f"   Assignee_Country.csv: {len(df_assignees)} rows")

    except FileNotFoundError:
        print(f"❌ File not found at: {input_excel_path}")
    except ImportError:
        print("❌ openpyxl library not installed. Run: pip install openpyxl")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
