import pandas as pd
from google.cloud import bigquery
from configs import GOOGLE_APPLICATION_CREDENTIALS
import re


def upload_to_bigquery(df, table_id, if_exists="replace"):
    client = bigquery.Client()
    
    job_config = bigquery.LoadJobConfig(write_disposition={
        "replace": bigquery.WriteDisposition.WRITE_TRUNCATE,
        "append": bigquery.WriteDisposition.WRITE_APPEND,
    }[if_exists])
    
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result() 
    print(f"✅ Uploaded {len(df)} rows to {table_id}")



def read_links_from_file(path_file):
    with open(path_file, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]
    return sorted(set(links))


def clean_column_names(df):
    df = df.copy()
    df.columns = [
        re.sub(r'\W+', '_', col) 
        .strip('_') 
        for col in df.columns
    ]
    return df
