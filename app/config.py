import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    groq_api_key = os.getenv("GROQ_API_KEY")
    gmail_user   = os.getenv("GMAIL_USER", "ticketsdata5@gmail.com")

settings = Settings()