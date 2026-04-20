import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm():
    return ChatOpenAI(
        model=os.getenv("MODEL_NAME"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        temperature=0
    )

# import os
# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI

# load_dotenv()

# def get_llm():
#     return ChatGoogleGenerativeAI(
#         model="gemini-2.5-flash-lite",
#         google_api_key=os.getenv("GOOGLE_API_KEY"),
#         temperature=0
#     )