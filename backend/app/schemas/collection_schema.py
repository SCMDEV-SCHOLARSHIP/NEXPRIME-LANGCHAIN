from pydantic import BaseModel

import app.cores.common_types as types


class RecordResponse(BaseModel, extra="forbid"):
    results: list[types.Record] | None = None
