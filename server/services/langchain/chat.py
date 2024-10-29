# File: /server/services/langchain/chat.py

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from server.services.langchain.llms.gemini import build_llm
from server.services.langchain.memories.memory import build_memory

def build_prompt():
    return ChatPromptTemplate(
        messages=[
            SystemMessage(content=(
                """
                Your are a teacher assistant. You are here to help students with their questions.
                """
            )),
            MessagesPlaceholder(variable_name="chat_history", n_messages=6),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ]
    )

def initialize_chat(conversation_id: str, chat_history: list):
    llm = build_llm()
    memory = build_memory(username=conversation_id, history=chat_history)
    prompt = build_prompt()
    
    tools = []
    
    agent = create_tool_calling_agent(
        llm=llm,
        prompt=prompt,
        tools=tools
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        return_intermediate_steps=True,
        verbose=True,
        handle_parsing_errors=True,
    )

    return agent_executor
