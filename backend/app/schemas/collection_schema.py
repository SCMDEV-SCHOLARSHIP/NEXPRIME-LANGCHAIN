from pydantic import BaseModel

import app.cores.common_types as types


class RecordResponse(BaseModel, extra="forbid"):
    results: list[types.Record] | None = None

class CollectionResponseDTO(BaseModel, extra="forbid"):
    collection_name: str