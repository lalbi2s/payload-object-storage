import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app import config


def make_client(endpoint_url: str | None):
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=config.S3_ACCESS_KEY,
        aws_secret_access_key=config.S3_SECRET_KEY,
        region_name=config.S3_REGION,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def get_client():
    return make_client(config.S3_ENDPOINT_URL)


def get_public_client():
    # Presigned URLs must use an address the caller can reach.
    return make_client(config.S3_PUBLIC_ENDPOINT)


def ensure_bucket() -> None:
    client = get_client()
    try:
        client.head_bucket(Bucket=config.S3_BUCKET)
    except ClientError:
        client.create_bucket(Bucket=config.S3_BUCKET)


def save_file(key: str, content: bytes, content_type: str, metadata: dict) -> None:
    get_client().put_object(
        Bucket=config.S3_BUCKET,
        Key=key,
        Body=content,
        ContentType=content_type,
        Metadata=metadata,
    )


def list_files() -> list[dict]:
    client = get_client()
    files = []
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=config.S3_BUCKET):
        for item in page.get("Contents", []):
            head = client.head_object(Bucket=config.S3_BUCKET, Key=item["Key"])
            files.append(
                {
                    "key": item["Key"],
                    "size": item["Size"],
                    "uploaded_at": item["LastModified"].isoformat(),
                    "metadata": head["Metadata"],
                }
            )
    return files


def file_exists(key: str) -> bool:
    try:
        get_client().head_object(Bucket=config.S3_BUCKET, Key=key)
    except ClientError:
        return False
    return True


def make_download_url(key: str, lifetime_seconds: int) -> str:
    return get_public_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": config.S3_BUCKET, "Key": key},
        ExpiresIn=lifetime_seconds,
    )
