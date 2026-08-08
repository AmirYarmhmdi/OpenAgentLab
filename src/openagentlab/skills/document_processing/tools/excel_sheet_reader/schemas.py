from pathlib import Path

from pydantic import BaseModel, Field

type ExcelCellValue = str | int | float | bool | None


class ExcelSheetReaderInput(BaseModel):
    path: Path
    sheet_name: str = Field(min_length=1)
    max_rows: int | None = Field(default=None, ge=1)


class ExcelSheetReaderOutput(BaseModel):
    path: Path
    sheet_name: str
    row_count: int = Field(ge=0)
    column_count: int = Field(ge=0)
    rows: tuple[tuple[ExcelCellValue, ...], ...]
    truncated: bool
