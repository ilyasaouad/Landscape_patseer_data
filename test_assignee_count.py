import pandas as pd


def test_assignee_count():
    # --- Read assignee count dataset ---
    assignee_csv_path = (
        r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\Assignee_Count.csv"
    )
    assignee_country_csv_path = (
        r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\Assignee_Country.csv"
    )


    print(assignee_csv_path)
    print(assignee_country_csv_path)
  

    df_assignee = pd.read_csv(assignee_csv_path, encoding="utf-8")
    df_assignee_country = pd.read_csv(assignee_country_csv_path, encoding="utf-8")

    print("Assignee data shape:", df_assignee.shape)
    print("Assignee_Country data shape:", df_assignee_country.shape)

 

if __name__ == "__main__":
    test_assignee_count()
