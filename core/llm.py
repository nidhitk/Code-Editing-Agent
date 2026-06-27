import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# def get_llm():
#     return ChatGroq(
#         model=os.getenv("MODEL_NAME"),
#         api_key=os.getenv("GROQ_API_KEY"),
#         temperature=0
#     )


from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_llm():
    return ChatGoogleGenerativeAI(
        model=os.getenv("MODEL_NAME"), # Defaults to flash if not set
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )