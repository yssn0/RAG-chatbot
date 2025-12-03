"""RAG pipeline implemented with Azure OpenAI + Pinecone"""

import logging
import time
import uuid
from typing import Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)

# --- Azure OpenAI ---
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

# --- Vector DB ---
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone

# --- Config ---
from .config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_CHAT_DEPLOYMENT,
    AZURE_EMBEDDING_DEPLOYMENT,

    PINECONE_API_KEY,
    PINECONE_DIMENSION,
    PINECONE_INDEX_NAME,
    PINECONE_NAMESPACE,
)

logger = logging.getLogger(__name__)

# --- Azure OpenAI Clients ---
embeddings = AzureOpenAIEmbeddings(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    azure_deployment=AZURE_EMBEDDING_DEPLOYMENT,
    api_version=AZURE_OPENAI_API_VERSION,
    model="text-embedding-ada-002",
)

# CORRECTION : Suppression de temperature=0.2
llm = AzureChatOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    azure_deployment=AZURE_CHAT_DEPLOYMENT,
    api_version=AZURE_OPENAI_API_VERSION,
    model=None,  
    streaming=False  
)


# --- Text Splitter ---
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    add_start_index=True,
)

# --- Pinecone Init ---
pc = Pinecone(api_key=PINECONE_API_KEY)

def _ensure_pinecone_index():
    existing = [i.name for i in pc.list_indexes()]
    if PINECONE_INDEX_NAME in existing:
        return

    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=PINECONE_DIMENSION,
        metric="cosine",
        spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
    )

    while True:
        idx = pc.describe_index(PINECONE_INDEX_NAME)
        if idx.status["ready"]:
            break
        time.sleep(1)

_ensure_pinecone_index()

# --- PDF Ingestion ---
def ingest_pdf(file_path: str, doc_id: Optional[str] = None) -> str:
    document_id = doc_id or str(uuid.uuid4())

    loader = PyPDFLoader(file_path)
    pages = loader.load()

    for i, page in enumerate(pages, 1):
        page.metadata["doc_id"] = document_id
        page.metadata["page_number"] = i

    chunks = text_splitter.split_documents(pages)

    PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=PINECONE_INDEX_NAME,
        namespace=PINECONE_NAMESPACE,
    )

    return document_id

# --- Retrieval ---
def get_retriever_for_doc(doc_id: Optional[str] = None):
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings,
        namespace=PINECONE_NAMESPACE,
    )

    search_kwargs = {"k": 5}
    
    if doc_id:
        search_kwargs["filter"] = {"doc_id": {"$eq": doc_id}}

    return vectorstore.as_retriever(search_kwargs=search_kwargs)

# --- Format Docs ---
def _format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# --- Prompt ---
DEFAULT_SYSTEM_PROMPT = (
    "You are an AI that answers questions using the document context only. "
    "If the answer is not in the context, say: 'I could not find that in the document.'"
)

# --- RAG Chain ---
def build_qa_chain(doc_id: Optional[str] = None):
    retriever = get_retriever_for_doc(doc_id)

    # CORRECTION : Fusion du System prompt dans le Human prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{system_prompt}\n\nContext:\n{context}\n\nQuestion: {question}")
        ]
    )

    answer_chain = (
        {
            "context": retriever | RunnableLambda(_format_docs),
            "question": RunnablePassthrough(),
            "system_prompt": lambda _: DEFAULT_SYSTEM_PROMPT,
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return RunnableParallel(
        answer=answer_chain,
        source_documents=retriever,
    )