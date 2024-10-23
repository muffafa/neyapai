from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory

def build_memory(username: str, history: list):
    memory = ChatMessageHistory()
    memory.messages = history
    return ConversationBufferMemory(
        chat_memory=memory,
        memory_key="chat_history",
        return_messages=True
    )
