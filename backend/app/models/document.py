from pydantic import BaseModel


class DocumentMeta(BaseModel):
    file_path: str
    category: str
    subject: str | None = None
    name: str
    stem: str
    ext: str
    total_split: int
    split_number: int
