# payload-object-storage

A small HTTP service that stores satellite images and calibration files in S3-compatible object storage. Each file is saved with its metadata (satellite, instrument, acquisition date) as S3 object metadata, so no database is needed.

The code only uses the S3 API. Locally it runs against SeaweedFS, and it also works with AWS S3.

## Stack

- Python 3.12
- FastAPI and uvicorn
- boto3
- SeaweedFS (S3 server, in docker-compose)
- pytest and moto for the tests

## Start the stack

```bash
docker compose up -d --build
```

The API is available on http://localhost:8000 (interactive docs on `/docs`) and the S3 endpoint on http://localhost:8333. The bucket `payload-files` is created at startup.

The access keys in `seaweedfs/s3.json`, `docker-compose.yml` and `.env.example` (`local-dev-access-key` and `local-dev-secret-key`) are fake values. They are for local development only. Never reuse them anywhere else.

Stop it with `docker compose down` (add `-v` to delete the stored files).

## Usage

Upload a file with its metadata:

```bash
curl -X POST http://localhost:8000/files \
  -F "file=@scene.tif" \
  -F "satellite=Sentinel-2A" \
  -F "instrument=MSI" \
  -F "acquisition_date=2026-03-14"
```

List the stored files:

```bash
curl http://localhost:8000/files
```

Get a download link valid for 60 seconds (default 300, maximum 3600):

```bash
curl "http://localhost:8000/files/<key>/download-url?expires=60"
```

Then download with the returned URL:

```bash
curl -o scene.tif "<url>"
```

Each file is stored under a unique key (a UUID followed by the file name), so two files with the same name never overwrite each other. The original name is kept in the metadata.

Upload rules:

- Allowed extensions: `.tif`, `.tiff`, `.png`, `.jpg`, `.fits`, `.cal`, `.csv`, `.json`
- Maximum size: 50 MB (change it with `MAX_UPLOAD_MB`)
- `acquisition_date` must be `YYYY-MM-DD`
- `satellite` and `instrument` must be ASCII text (S3 metadata limitation)

## Run the tests

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

S3 is mocked with moto, so no SeaweedFS and no network are needed.

## Configuration

Settings are read from environment variables, see `.env.example`. To use AWS S3 instead of SeaweedFS, leave `S3_ENDPOINT_URL` and `S3_PUBLIC_ENDPOINT` empty and set real credentials, bucket and region in your environment.

`S3_PUBLIC_ENDPOINT` is the address used to sign download links. Inside docker the API reaches SeaweedFS at `http://seaweedfs:8333`, but a browser or curl on your machine needs `http://localhost:8333`.

## Possible improvements

- Stream large uploads instead of reading them in memory
- Filter the file list by satellite or date
- Pagination on the list endpoint
- Authentication
