import boto3

AWS_ACCESS_KEY_ID = "your-aws-access-key"
AWS_SECRET_ACCESS_KEY = "your-aws-secret-key"
AWS_REGION = ""

def configure_client(service: str):
    """
    configure boto3 client for aws
    :return: configured boto client
    """

    boto_client = boto3.client(
        service,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    return boto_client


def configure_resource(service: str):
    boto_client = boto3.resource(
        service,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    return boto_client


S3_CLIENT = configure_client("s3")
TEXTRACT_CLIENT = configure_client("textract")
SHORT_URL_TABLE = configure_resource("dynamodb").Table("url_redirect")
