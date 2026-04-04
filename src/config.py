import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # إعدادات RAG
    CHUNK_SIZE = 1500
    CHUNK_OVERLAP = 300
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    COLLECTION_NAME = "general_doc_rag"
    