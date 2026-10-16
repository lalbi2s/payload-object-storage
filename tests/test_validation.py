import pytest

from app import config
from app.validation import (
    ValidationError,
    check_date,
    check_extension,
    check_size,
    clean_filename,
    make_object_key,
)


def test_allowed_extension_passes():
    check_extension("image.TIF")


def test_unknown_extension_is_rejected():
    with pytest.raises(ValidationError):
        check_extension("virus.exe")


def test_file_without_extension_is_rejected():
    with pytest.raises(ValidationError):
        check_extension("README")


def test_size_over_limit_is_rejected():
    with pytest.raises(ValidationError):
        check_size(config.MAX_UPLOAD_BYTES + 1)


def test_size_at_limit_passes():
    check_size(config.MAX_UPLOAD_BYTES)


def test_valid_date_passes():
    check_date("2026-03-14")


def test_bad_date_is_rejected():
    with pytest.raises(ValidationError):
        check_date("14/03/2026")


def test_clean_filename_removes_path_and_odd_characters():
    assert clean_filename("../../etc/my image (1).png") == "my_image__1_.png"


def test_same_filename_gives_different_keys():
    first = make_object_key("scene.tif")
    second = make_object_key("scene.tif")
    assert first != second
    assert first.endswith("-scene.tif")
