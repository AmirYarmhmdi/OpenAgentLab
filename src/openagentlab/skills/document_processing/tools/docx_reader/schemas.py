from pathlib import Path

from pydantic import BaseModel, Field


class DOCXReaderInput(BaseModel):
    path: Path


class DOCXParagraph(BaseModel):
    index: int = Field(ge=1)
    text: str


class DOCXTable(BaseModel):
    index: int = Field(ge=1)
    rows: tuple[tuple[str, ...], ...]


class DOCXReaderOutput(BaseModel):
    path: Path
    paragraphs: tuple[DOCXParagraph, ...]
    tables: tuple[DOCXTable, ...]
    paragraph_count: int = Field(ge=0)
    table_count: int = Field(ge=0)
    metadata: dict[str, str | None]
