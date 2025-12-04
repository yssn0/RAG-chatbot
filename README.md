### 🏗️ Architecture Technique

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