import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from app import config
from app.main import app

FORM = {"satellite": "Sentinel-2A", "instrument": "MSI", "acquisition_date": "2026-03-14"}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(config, "S3_ENDPOINT_URL", None)
    monkeypatch.setattr(config, "S3_PUBLIC_ENDPOINT", None)
    with mock_aws():
        with TestClient(app) as test_client:
            yield test_client


def upload(client, name="scene.tif", content=b"data", form=FORM):
    return client.post("/files", files={"file": (name, content)}, data=form)


def test_upload_returns_key_and_metadata(client):
    response = upload(client)
    assert response.status_code == 201
    body = response.json()
    assert body["key"].endswith("-scene.tif")
    assert body["metadata"]["satellite"] == "Sentinel-2A"
    assert body["metadata"]["original-filename"] == "scene.tif"


def test_same_filename_twice_creates_two_objects(client):
    first = upload(client).json()["key"]
    second = upload(client).json()["key"]
    assert first != second
    assert len(client.get("/files").json()) == 2


def test_list_shows_metadata(client):
    upload(client)
    files = client.get("/files").json()
    assert files[0]["metadata"]["instrument"] == "MSI"
    assert files[0]["metadata"]["acquisition-date"] == "2026-03-14"
    assert files[0]["size"] == 4


def test_upload_rejects_unknown_file_type(client):
    response = upload(client, name="notes.exe")
    assert response.status_code == 422
    assert client.get("/files").json() == []


def test_upload_rejects_file_over_size_limit(client, monkeypatch):
    monkeypatch.setattr(config, "MAX_UPLOAD_BYTES", 10)
    response = upload(client, content=b"x" * 11)
    assert response.status_code == 422


def test_upload_rejects_bad_date(client):
    response = upload(client, form={**FORM, "acquisition_date": "yesterday"})
    assert response.status_code == 422


def test_upload_requires_metadata(client):
    response = client.post("/files", files={"file": ("scene.tif", b"data")})
    assert response.status_code == 422


def test_download_url_has_requested_lifetime(client):
    key = upload(client).json()["key"]
    response = client.get(f"/files/{key}/download-url", params={"expires": 120})
    assert response.status_code == 200
    assert response.json()["expires_in"] == 120
    assert "X-Amz-Expires=120" in response.json()["url"]
    assert key in response.json()["url"]


def test_download_url_lifetime_is_capped(client):
    key = upload(client).json()["key"]
    response = client.get(f"/files/{key}/download-url", params={"expires": 999999})
    assert response.status_code == 422


def test_download_url_for_missing_file_returns_404(client):
    response = client.get("/files/does-not-exist.tif/download-url")
    assert response.status_code == 404
