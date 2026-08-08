from pathlib import Path

from pydantic import BaseModel, Field


class ExcelWorkbookReaderInput(BaseModel):
    path: Path


class ExcelSheetInfo(BaseModel):
    name: str
    index: int = Field(ge=1)
    max_row: int = Field(ge=0)
    max_column: int = Field(ge=0)


class ExcelWorkbookReaderOutput(BaseModel):
    path: Path
    sheet_count: int = Field(ge=0)
    sheets: tuple[ExcelSheetInfo, ...]
    metadata: dict[str, str | None]
