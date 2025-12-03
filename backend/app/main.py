import os
import shutil
import logging
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# On enlève StreamingResponse
from pydantic import BaseModel

from .rag_pipeline import ingest_pdf, build_qa_chain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Chatbot Workshop")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    doc_id: Optional[str] = None
    question: str
    history: Optional[List[ChatMessage]] = None

# On réintroduit le modèle de réponse structurée
class ChatResponse(BaseModel):
    answer: str
    sources: Optional[list] = None

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF.")

    temp_dir = "tmp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        logger.info(f"Processing file: {file.filename}")
        doc_id = ingest_pdf(file_path)
        logger.info(f"File processed with ID: {doc_id}")
    except Exception as e:
        logger.error(f"Error ingesting PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return {"doc_id": doc_id, "message": "PDF processed successfully"}


# MODIFICATION ICI : Endpoint classique (plus de streaming)
@app.post("/chat", response_model=ChatResponse)
async def chat_with_doc(request: ChatRequest):
    """
    Ask a question about uploaded documents.
    Standard (Non-streaming) response for compatibility with o1 models.
    """
    try:
        qa_chain = build_qa_chain(request.doc_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building QA chain: {e}")

    history_text = ""
    if request.history:
        for msg in request.history:
            prefix = "User" if msg.role == "user" else "Assistant"
            history_text += f"{prefix}: {msg.content}\n"

    question_with_history = history_text + f"User: {request.question}"

    # Exécution simple (invoke au lieu de astream)
    try:
        result = qa_chain.invoke(question_with_history)
        answer = result["answer"]
        
        # Optionnel : récupérer les sources si besoin
        sources = []
        if "source_documents" in result:
             for doc in result["source_documents"]:
                 sources.append({"content": doc.page_content[:200] + "..."})

        return ChatResponse(answer=answer, sources=sources)
        
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        raise HTTPException(status_code=500, detail=str(e))