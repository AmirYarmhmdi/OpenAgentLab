from pathlib import Path

from pydantic import BaseModel, Field

type JSONScalar = str | int | float | bool | None
type JSONValue = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]


class JSONReaderInput(BaseModel):
    path: Path
    encoding: str = Field(default="utf-8", min_length=1)


class JSONReaderOutput(BaseModel):
    path: Path
    data: JSONValue
    encoding: str
    root_type: str
    item_count: int | None
