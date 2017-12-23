import csv

from google.cloud import bigquery, storage
from google.cloud.bigquery import LoadJobConfig
from google.cloud.bigquery import SchemaField
from data_collecter import bus_res_keys
from config import PROJECT_ID, BUCKET

date_cols = [u'dc:date', u'dct:valid', u'odpt:fromBusstopPoleTime']

def create_bq_schema():
    schema = []
    for col in bus_res_keys:
        name = col.split(':')[-1]
        if col in date_cols:
            type = "TIMESTAMP"
        else:
            type = "STRING"
        x = SchemaField(name, type)
        schema.append(x)
    return schema

if __name__ == '__main__':
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET)

    client = bigquery.Client()
    table_ref = client.dataset('bus').table('bus')

    load_config = LoadJobConfig()
    load_config.skip_leading_rows = 1
    load_config.schema = create_bq_schema()

    for blob in bucket.list_blobs():
        jobname = blob.name
        uri = "gs://{bucket}/{filename}".format(bucket=BUCKET, filename=blob.name)
        job = client.load_table_from_storage(
                jobname, uri, table_ref, job_config=load_config)
        job.begin()
        job.result()