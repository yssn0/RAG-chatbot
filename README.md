### 🏗️ Architecture Technique

The application is built on a decoupled architecture separating the client interface from the inference logic.

<p align="center">
  <img src="assets/architecture_visual.png" alt="RAG Architecture Flow" width="100%">
</p>

### 🛠️ Tech Stack & Flow

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | **Next.js** | Handles UI rendering and manages the chat state. |
| **Backend** | **FastAPI** | Orchestrates the RAG logic and handles API endpoints. |
| **Vector DB** | **Pinecone** | Stores document embeddings for semantic search retrieval. |
| **LLM** | **Azure OpenAI** | Provides Embedding models (Ada-002) and Chat models (GPT-3.5/4). |