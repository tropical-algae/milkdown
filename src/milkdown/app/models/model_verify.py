from pydantic import BaseModel


class VerifyRequest(BaseModel):
    timestamp: int
    version: str


class VerifyResponse(BaseModel):
    status: bool
    message: str  
