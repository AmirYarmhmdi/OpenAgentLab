from pathlib import Path

from pydantic import BaseModel, Field


class CSVReaderInput(BaseModel):
    path: Path
    delimiter: str | None = Field(default=None, min_length=1, max_length=1)
    encoding: str = Field(default="utf-8", min_length=1)
    max_rows: int | None = Field(default=None, ge=1)


class CSVReaderOutput(BaseModel):
    path: Path
    row_count: int = Field(ge=0)
    column_count: int = Field(ge=0)
    rows: tuple[tuple[str, ...], ...]
    delimiter: str
    encoding: str
    truncated: bool
