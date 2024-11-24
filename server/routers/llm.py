from fastapi import APIRouter, HTTPException
from server.models.llm import LLMRequest, LLMResponse
from server.services.langchain.agents.data_agent import DataAnalysisAgent

router = APIRouter(prefix="/llm", tags=["LLM"])

# Initialize agent
data_agent = DataAnalysisAgent()

@router.post("/completions", response_model=LLMResponse)
async def get_completion(request: LLMRequest):
    try:
        response, thought_process = await data_agent.process_query(request.input)
        return LLMResponse(
            output=response,
            thought_process=thought_process
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
