from langchain_google_genai import ChatGoogleGenerativeAI
import os

def build_llm():
    api_key = os.getenv("GEMINI_API_KEY")
    print("API KEY", api_key)
    return ChatGoogleGenerativeAI(api_key=api_key, model="gemini-1.5-flash", temperature=0, verbose=True)

build_llm()
