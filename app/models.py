from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=3, max_length=100)
    message: str = Field(min_length=1, max_length=4000)


class SourceItem(BaseModel):
    filename: str
    display_name: str | None = None
    authority: str | None = None
    score: float | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceItem] = []
