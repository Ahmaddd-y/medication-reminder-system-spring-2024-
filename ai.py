from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def get_llm(model_type="cloud"):
    if model_type == "cloud":
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=GEMINI_KEY)
    elif model_type == "local":
        return ChatOllama(model="qwen2.5:3b")
    else:
        raise ValueError("Unknown model type")

def check_interaction(drugs: list, model_type="cloud"):
    llm = get_llm(model_type)
    prompt = f"Is it safe to take {', '.join(drugs)} together? Explain VERY briefly like you're talking to a patient."
    return llm.invoke(prompt)
