import boto3
from botocore.exceptions import ClientError
import json

def get_secret():

    secret_name = "LLM_API_Keys"
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret_api_keys = get_secret_value_response['SecretString']
    secrets = json.loads(secret_api_keys)
    return secrets
    # print(f"Secrets: \n {secrets}")
    # secret_google_api_key = secrets['GEMINI_API_KEY']

    # print(f"Gemini api key: \n{secret_google_api_key}")

# api_key = get_secret()

