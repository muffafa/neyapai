from pydantic import BaseModel
from typing import List, Optional

class LLMRequest(BaseModel):
    input: str

class LLMResponse(BaseModel):
    output: str
    thought_process: Optional[List[dict]] = None