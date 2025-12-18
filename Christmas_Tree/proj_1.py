import os
import pandas as pd
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

# Global variables
WIKI_URL = "https://en.wikipedia.org/wiki/Rockefeller_Center_Christmas_Tree"
DATASET_ID = "xmas"
TABLE_ID = "tree"

def get_wiki_data(url: str) -> pd.DataFrame:
    """Extracts the first wikitable from a given Wikipedia URL."""
    try:
        tables = pd.read_html(url, attrs={'class': 'wikitable'})
        print(f"Extracted {len(tables)} wikitables.")
        return tables[0]
    except Exception as e:
        print(f"Error extracting data: {e}")
        raise

def clean_tree_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans the dataframe: handles nulls, removes citations, and renames columns."""
    # 1. Handle missing values
    df['Original location'] = df['Original location'].fillna('No location provided')
    
    # 2. Clean citations (e.g., [1], [2]) from specific columns
  
    target_cols = ['Original location', 'Height']
    for col in target_cols:
        df[col] = df[col].astype(str).str.replace(r'\[.*\]', '', regex=True).str.strip()

    # 3. Drop unnecessary columns and rename for BigQuery compatibility
    df = df.drop(columns=['Lighting ceremony/Misc'], errors='ignore')
    df.rename(columns={
        'Original location': 'Original_location', 
        'Tree type': 'Tree_type'
    }, inplace=True)
    
    return df

def load_to_bigquery(df: pd.DataFrame, table_id: str):
    """Loads a pandas DataFrame into a BigQuery table."""
    client = bigquery.Client()
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        autodetect=True,
        ignore_unknown_values=True
    )

    try:
        print(f"Starting load job for table: {table_id}...")
        job = client.load_table_from_dataframe(
            df, 
            table_id, 
            location='US', 
            job_config=job_config
        )
        job.result()  # Wait for the job to complete
        print("The job has loaded successfully. Happy holidays!")
    except GoogleAPIError as e:
        print(f"BigQuery load failed: {e}")
        raise

def main():
    """Main execution flow."""
  
    # **Set the environmental variable in your terminal environment to integrate with Google Cloud Platform (GCP).
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account.json"
    
    raw_df = get_wiki_data(WIKI_URL)
    cleaned_df = clean_tree_data(raw_df)
    load_to_bigquery(cleaned_df, TABLE_ID)

if __name__ == "__main__":
    main()
