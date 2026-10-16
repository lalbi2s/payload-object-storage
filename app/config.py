import os

S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL")
S3_PUBLIC_ENDPOINT = os.environ.get("S3_PUBLIC_ENDPOINT") or S3_ENDPOINT_URL
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY", "local-dev-access-key")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY", "local-dev-secret-key")
S3_BUCKET = os.environ.get("S3_BUCKET", "payload-files")
S3_REGION = os.environ.get("S3_REGION", "us-east-1")

MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_MB", "50")) * 1024 * 1024
ALLOWED_EXTENSIONS = {".tif", ".tiff", ".png", ".jpg", ".fits", ".cal", ".csv", ".json"}

DEFAULT_URL_LIFETIME = 300
MAX_URL_LIFETIME = 3600
