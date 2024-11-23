import os

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_default_key")
    OPENAI_URL = "https://api.openai.com/v1/chat/completions"
    DEBUG = True
