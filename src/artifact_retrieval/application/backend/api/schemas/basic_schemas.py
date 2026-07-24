from pydantic import BaseModel

class ChatRequest(BaseModel):
    content: str

class ChatResponse(BaseModel):
    content: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatHistory(BaseModel):
    messages: list[ChatMessage]
    