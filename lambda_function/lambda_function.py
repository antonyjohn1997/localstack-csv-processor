import json
import boto3
import pandas as pd
from datetime import datetime
from io import StringIO

s3_client = boto3.client("s3", endpoint_url="http://localhost:4566")
dynamodb = boto3.resource("dynamodb", endpoint_url="http://localhost:4566")
table_name = "CSV_Metadata"

def lambda_handler(event, context):
    try:
        # Get S3 event details
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']
        
        # Get file content from S3
        file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = file_obj["Body"].read().decode("utf-8")

        # Read CSV into Pandas DataFrame
        df = pd.read_csv(StringIO(file_content))

        # Extract metadata
        metadata = {
            "filename": file_key,
            "upload_timestamp": str(datetime.utcnow()),
            "file_size_bytes": file_obj["ContentLength"],
            "row_count": len(df),
            "column_count": len(df.columns),
            "column_names": list(df.columns)
        }

        # Store metadata in DynamoDB
        table = dynamodb.Table(table_name)
        table.put_item(Item=metadata)

        return {
            "statusCode": 200,
            "body": json.dumps("Metadata stored successfully")
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error processing file: {str(e)}")
        }
