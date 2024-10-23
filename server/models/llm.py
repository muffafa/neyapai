from pydantic import BaseModel

class LLMRequest(BaseModel):
    input: str

class LLMResponse(BaseModel):
    output: str
    intermediate_steps: list[str] = []