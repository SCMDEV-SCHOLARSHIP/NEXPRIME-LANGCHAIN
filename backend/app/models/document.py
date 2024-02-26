from pydantic import BaseModel


class DocumentMeta(BaseModel, extra="forbid"):
    file_id: int
    source: str
    category: str
    subject: str | None = None
    name: str
    stem: str
    ext: str
    total_split: int
    split_number: int
