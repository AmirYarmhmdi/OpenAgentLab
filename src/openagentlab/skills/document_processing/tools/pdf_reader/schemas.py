from pathlib import Path

from pydantic import BaseModel, Field


class PDFReaderInput(BaseModel):
    path: Path


class PDFPage(BaseModel):
    page_number: int = Field(ge=1)
    text: str


class PDFReaderOutput(BaseModel):
    path: Path
    page_count: int = Field(ge=0)
    pages: tuple[PDFPage, ...]
    metadata: dict[str, str | None]
