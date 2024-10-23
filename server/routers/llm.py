from fastapi import APIRouter, HTTPException, Depends
from server.models.llm import LLMRequest, LLMResponse
from server.services.langchain.chat import initialize_chat
import logging

router = APIRouter(
    prefix="/llm",
    tags=["LLM"]
)

# Set up logging
logger = logging.getLogger(__name__)

@router.post("/completions", response_model=LLMResponse)
async def llm_completions(request: LLMRequest):
    """
    Endpoint to invoke the LLM and get completions.
    """
    try:
        agent_executor = initialize_chat(
            conversation_id="_",  # Placeholder
            chat_history=[],
        )
        
        # Invoke the LLM with user input
        response = await agent_executor.ainvoke({"input": request.input})
        
        # Extract the output from the response
        llm_output = response.get("output", "No response generated.")
        
        return LLMResponse(output=llm_output)
    
    except Exception as e:
        logger.error(f"Error in llm_completions endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
