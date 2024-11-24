from fastapi import APIRouter, HTTPException, BackgroundTasks
from server.models.llm import LLMRequest, LLMResponse
from server.services.langchain.agents.data_agent import DataAnalysisAgent
import logging
from typing import Optional
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["LLM"])

# Initialize agent
data_agent = DataAnalysisAgent()

# Rate limiting için basit bir cache
request_cache = {}
RATE_LIMIT_SECONDS = 2  # Her kullanıcı için minimum istek aralığı

def clean_old_requests(current_time: float, max_age: int = 3600):
    """Eski istekleri temizle"""
    for user_id in list(request_cache.keys()):
        if current_time - request_cache[user_id] > max_age:
            del request_cache[user_id]

@router.post("/completions", response_model=LLMResponse)
async def get_completion(
    request: LLMRequest,
    background_tasks: BackgroundTasks,
    user_id: Optional[str] = "default"
):
    try:
        # Rate limiting kontrolü
        current_time = time.time()
        if user_id in request_cache:
            time_since_last_request = current_time - request_cache[user_id]
            if time_since_last_request < RATE_LIMIT_SECONDS:
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many requests. Please wait {RATE_LIMIT_SECONDS - time_since_last_request:.1f} seconds."
                )
        
        # İstek zamanını güncelle
        request_cache[user_id] = current_time
        
        # Eski istekleri temizle
        background_tasks.add_task(clean_old_requests, current_time)
        
        # İsteği işle
        response, thought_process = await data_agent.process_query(request.input)
        
        return LLMResponse(
            output=response,
            thought_process=thought_process
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
