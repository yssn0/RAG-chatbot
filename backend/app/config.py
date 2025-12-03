import os
from dotenv import load_dotenv

load_dotenv()

# --- Azure OpenAI Settings ---
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

AZURE_CHAT_DEPLOYMENT = os.getenv("AZURE_CHAT_DEPLOYMENT")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")

# --- Pinecone Settings ---
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "pdf-rag-index")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "")
PINECONE_DIMENSION = int(os.getenv("PINECONE_DIMENSION", "1536"))

print("Loaded Azure Endpoint:", AZURE_OPENAI_ENDPOINT)
print("Loaded Chat Deployment:", AZURE_CHAT_DEPLOYMENT)
print("Loaded Embed Deployment:", AZURE_EMBEDDING_DEPLOYMENT)
