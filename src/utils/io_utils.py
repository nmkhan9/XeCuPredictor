import pandas as pd
from google.cloud import bigquery


def upload_to_bigquery(df, table_id, if_exists="replace"):
    client = bigquery.Client()
    job = client.load_table_from_dataframe(df, table_id)
    job.result()
    print(f"✅ Uploaded to {table_id}")
