from app.schemas.message_schema import MessageIdentifierRequest


class ReconstructionRequest(MessageIdentifierRequest, extra="forbid"):
    llm_model: str
    memory_type: str = "buffer_window"
    cut_off: int = 6
