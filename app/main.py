from contextlib import asynccontextmanager
from urllib.parse import quote, unquote

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile

from app import config, storage, validation


@asynccontextmanager
async def lifespan(app: FastAPI):
    storage.ensure_bucket()
    yield


app = FastAPI(title="payload-object-storage", lifespan=lifespan)


@app.post("/files", status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    satellite: str = Form(...),
    instrument: str = Form(...),
    acquisition_date: str = Form(...),
):
    filename = file.filename or ""
    try:
        validation.check_extension(filename)
        validation.check_text(satellite, "satellite")
        validation.check_text(instrument, "instrument")
        validation.check_date(acquisition_date)
        # Read one byte more than the limit so we can detect a file that is too big.
        content = await file.read(config.MAX_UPLOAD_BYTES + 1)
        validation.check_size(len(content))
    except validation.ValidationError as error:
        raise HTTPException(status_code=422, detail=str(error))

    key = validation.make_object_key(filename)
    metadata = {
        "satellite": satellite,
        "instrument": instrument,
        "acquisition-date": acquisition_date,
        "original-filename": quote(filename),
    }
    storage.save_file(key, content, file.content_type or "application/octet-stream", metadata)
    return {"key": key, "size": len(content), "metadata": _readable(metadata)}


@app.get("/files")
def list_files():
    files = storage.list_files()
    for item in files:
        item["metadata"] = _readable(item["metadata"])
    return files


@app.get("/files/{key}/download-url")
def get_download_url(
    key: str,
    expires: int = Query(config.DEFAULT_URL_LIFETIME, ge=1, le=config.MAX_URL_LIFETIME),
):
    if not storage.file_exists(key):
        raise HTTPException(status_code=404, detail="File not found")
    return {"url": storage.make_download_url(key, expires), "expires_in": expires}


def _readable(metadata: dict) -> dict:
    result = dict(metadata)
    if "original-filename" in result:
        result["original-filename"] = unquote(result["original-filename"])
    return result
