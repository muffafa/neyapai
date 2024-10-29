from fastapi import APIRouter, HTTPException, Depends
from server.models.llm import LLMRequest, LLMResponse
from server.models.chat import Message, ChatHistory
from server.services.langchain.chat import initialize_chat
from server.database import db
from datetime import datetime
import logging

router = APIRouter(
    prefix="/llm",
    tags=["LLM"]
)

# Set up logging
logger = logging.getLogger(__name__)

chat_collection = db.get_collection("chat_history")

@router.post("/completions", response_model=LLMResponse)
async def llm_completions(request: LLMRequest, user_id: str = "default_user"):
    """
    Endpoint to invoke the LLM and get completions.
    """
    try:
        # Fetch or create chat history
        chat_history = await chat_collection.find_one({"user_id": user_id})
        
        # Initialize messages list
        messages_list = []
        if chat_history and "messages" in chat_history:
            messages_list = [
                {
                    "role": msg.get("role", ""),
                    "content": msg.get("content", "")
                }
                for msg in chat_history["messages"]
                if "role" in msg and "content" in msg
            ]
        
        # Initialize chat if no history exists
        if not chat_history:
            new_chat = ChatHistory(user_id=user_id)
            await chat_collection.insert_one(new_chat.dict(by_alias=True))
        
        # Initialize chat with history
        agent_executor = initialize_chat(
            conversation_id=user_id,
            chat_history=messages_list
        )
        
        # Create new message
        new_message = Message(role="user", content=request.input)
        
        try:
            # Invoke the LLM
            response = await agent_executor.ainvoke({"input": request.input})
            llm_output = response.get("output", "No response generated.")
        except Exception as e:
            logger.error(f"LLM invocation error: {str(e)}")
            llm_output = "I apologize, but I encountered an error processing your request."
        
        # Create assistant message
        assistant_message = Message(role="assistant", content=llm_output)
        
        # Update chat history
        update_result = await chat_collection.update_one(
            {"user_id": user_id},
            {
                "$push": {
                    "messages": {
                        "$each": [
                            new_message.dict(),
                            assistant_message.dict()
                        ]
                    }
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if not update_result.modified_count:
            logger.error("Failed to update chat history")
        
        return LLMResponse(output=llm_output)
    
    except Exception as e:
        logger.error(f"Error in llm_completions endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/history/{user_id}")
async def get_chat_history(user_id: str):
    """
    Get chat history for a specific user
    """
    chat_history = await chat_collection.find_one({"user_id": user_id})
    if not chat_history:
        return {"messages": []}
    return chat_history
