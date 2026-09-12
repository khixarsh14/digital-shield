"""Bound multipart ingestion before parsing and close temporary upload handles."""

import os
from pathlib import PurePath

from fastapi import HTTPException, Request
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile

from backend.tools.vision_tool import analyze_image, analyze_video
from backend.agent.verifier import verify_media
from backend.models.schemas import Language


FORMATS = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
           ".webp": "image/webp", ".mp4": "video/mp4", ".mov": "video/quicktime",
           ".webm": "video/webm"}


def max_upload_bytes() -> int:
    try:
        mb = int(os.getenv("MAX_MEDIA_UPLOAD_MB", "10"))
    except ValueError:
        mb = 10
    return max(1, min(mb, 12)) * 1024 * 1024


def validate_media(filename: str, mime: str, data: bytes) -> str:
    expected = FORMATS.get(PurePath(filename).suffix.lower())
    if not expected or mime.lower() != expected:
        raise HTTPException(415, "Unsupported media extension or MIME type.")
    valid = False
    if expected == "image/png":
        valid = data.startswith(b"\x89PNG\r\n\x1a\n")
    elif expected == "image/jpeg":
        valid = data.startswith(b"\xff\xd8\xff")
    elif expected == "image/webp":
        valid = data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    elif expected in {"video/mp4", "video/quicktime"}:
        box_size = int.from_bytes(data[:4], "big")
        brands = data[8:12] + data[16:min(box_size, 256)]
        valid = data[4:8] == b"ftyp" and 16 <= box_size <= len(data)
        valid = valid and (b"qt  " in brands if expected == "video/quicktime" else
                          any(brand in brands for brand in (b"isom", b"iso2", b"mp41", b"mp42", b"avc1")))
    elif expected == "video/webm":
        valid = data.startswith(b"\x1a\x45\xdf\xa3") and b"webm" in data[:4096]
    if not valid:
        raise HTTPException(415, "File contents do not match a supported media format.")
    return expected


async def process_upload(request: Request, verify: bool = False, language: Language = "en"):
    limit = max_upload_bytes()
    # Enforce even for chunked requests; the allowance is for multipart headers.
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > limit + 65536:
            raise HTTPException(413, "Media upload exceeds the configured size limit.")
        body.extend(chunk)

    async def receive():
        return {"type": "http.request", "body": bytes(body), "more_body": False}

    buffered = Request(request.scope, receive)
    try:
        async with buffered.form(max_files=1, max_fields=0) as form:
            file = form.get("file")
            if not isinstance(file, UploadFile) or len(form.multi_items()) != 1:
                raise HTTPException(422, "Provide exactly one uploaded file in the file field.")
            data = await file.read(limit + 1)
            if len(data) > limit:
                raise HTTPException(413, "Media upload exceeds the configured size limit.")
            if not data:
                raise HTTPException(422, "Uploaded media is empty.")
            mime = validate_media(file.filename or "", file.content_type or "", data)
            if verify:
                return await run_in_threadpool(verify_media, data, mime, language)
            tool = analyze_image if mime.startswith("image/") else analyze_video
            return await run_in_threadpool(tool, data, mime)
    except HTTPException:
        raise
    except (ValueError, OSError):
        raise HTTPException(400, "Media upload could not be read.") from None
