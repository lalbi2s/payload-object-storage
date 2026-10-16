import os
import re
import uuid
from datetime import date

from app import config


class ValidationError(Exception):
    pass


def check_extension(filename: str) -> None:
    extension = os.path.splitext(filename)[1].lower()
    if extension not in config.ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(config.ALLOWED_EXTENSIONS))
        raise ValidationError(f"File type '{extension}' is not allowed. Allowed: {allowed}")


def check_size(size: int) -> None:
    if size > config.MAX_UPLOAD_BYTES:
        max_mb = config.MAX_UPLOAD_BYTES // (1024 * 1024)
        raise ValidationError(f"File is too large. Maximum size is {max_mb} MB")


def check_date(value: str) -> None:
    try:
        date.fromisoformat(value)
    except ValueError:
        raise ValidationError("acquisition_date must use the format YYYY-MM-DD")


def clean_filename(filename: str) -> str:
    name = os.path.basename(filename)
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)


def make_object_key(filename: str) -> str:
    return f"{uuid.uuid4()}-{clean_filename(filename)}"
