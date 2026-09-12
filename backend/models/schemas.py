from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints


Language = Literal["en", "ur"]
RiskStatus = Literal["green", "yellow", "red"]
NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class VerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: NonEmptyText = Field(description="Message, claim, or URL to verify.")
    language: Language = "en"
    session_id: NonEmptyText | None = Field(
        default=None, description="Reserved for future follow-up handling; not stored."
    )


class Source(BaseModel):
    label: str
    url: HttpUrl


class VerifyResponse(BaseModel):
    status: RiskStatus
    label: str
    summary: str
    reasons: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    needs_followup: bool = False
    followup_question: str | None = None
    language: Language


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["digital-shield"] = "digital-shield"
