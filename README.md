### 🏗️ Architecture Technique

The application is built on a decoupled architecture separating the client interface from the inference logic.

Here is the flow of data through the RAG pipeline:

```mermaid
graph LR
    User[Utilisateur] -->|Question| UI[Frontend Next.js]
    UI -->|API Request| API[Backend FastAPI]
    
    subgraph "Azure Cloud & Services"
        API -->|1. Embed Query| OAI[Azure OpenAI]
        API -->|2. Search Vectors| PC[Pinecone Vector DB]
        PC -->|3. Return Context| API
        API -->|4. Send Prompt + Context| OAI
        OAI -->|5. Answer| API
    end
    
    API -->|Réponse Streamée| UI

<p align="center">
  <img src="assets/architecture_visual.png" alt="Architecture Diagram" width="100%">
</p>

### 🛠️ Tech Stack & Flow

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | **Next.js** | Handles UI rendering and manages the chat state. |
| **Backend** | **FastAPI** | Orchestrates the RAG logic and handles API endpoints. |
| **Vector DB** | **Pinecone** | Stores document embeddings for semantic search retrieval. |
| **LLM** | **Azure OpenAI** | Provides Embedding models (Ada-002) and Chat models (GPT-3.5/4). |


