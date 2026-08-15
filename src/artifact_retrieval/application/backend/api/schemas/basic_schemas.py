from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    content: str

class ChatResponse(BaseModel):
    content: str
    sources: list[dict] = Field(default_factory=list) 

class ChatMessage(BaseModel):
    role: str
    content: str
    sources: list[dict] = Field(default_factory=list)

class ChatHistory(BaseModel):
    messages: list[ChatMessage]
    