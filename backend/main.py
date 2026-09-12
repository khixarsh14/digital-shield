import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.models.schemas import HealthResponse, Language, VerifyRequest, VerifyResponse
from starlette.concurrency import run_in_threadpool
from backend.agent.verifier import verify_content
from backend.models.media import MediaAnalysis
from backend.utils.media_upload import process_upload


app = FastAPI(title="Digital Shield", version="0.1.0")

frontend_origins = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in frontend_origins.split(",") if origin.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@app.post("/verify", response_model=VerifyResponse)
async def verify(request: VerifyRequest) -> VerifyResponse:
    return await run_in_threadpool(verify_content, request)


@app.post("/analyze-media", response_model=MediaAnalysis | VerifyResponse, openapi_extra={
    "requestBody": {"required": True, "content": {"multipart/form-data": {
        "schema": {"type": "object", "required": ["file"], "properties": {
            "file": {"type": "string", "format": "binary"}
        }}
    }}}
})
async def analyze_media(request: Request, verify: bool = False, language: Language = "en") -> MediaAnalysis | VerifyResponse:
    return await process_upload(request, verify=verify, language=language)
