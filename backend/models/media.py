from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TimestampObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    time: str = Field(pattern=r"^\d{2,}:[0-5]\d(?:\.[0-9]+)?$")
    observation: str


class MediaEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str
    visible_text: str
    spoken_text: str
    urls: list[str]
    claims: list[str]
    organizations: list[str]
    signals: list[str]
    observations: list[str]
    timestamps: list[TimestampObservation]
    confidence: Literal["low", "medium", "high"]
    manipulation_assessment: Literal[
        "possible_manipulation", "no_clear_manipulation_evidence", "unable_to_determine"
    ]


class MediaAnalysis(BaseModel):
    media_type: Literal["image", "video"]
    status: Literal["analyzed", "unavailable", "invalid_response"]
    evidence: MediaEvidence | None = None
    explanation: str
