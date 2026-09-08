# AI IT Helpdesk Agent - Backend

FastAPI backend for the AI IT Helpdesk application with AI-powered agent capabilities.

## Architecture

```
ai-it-helpdesk-agent/backend/
├── app/
│   ├── main.py                          # FastAPI app + CORS + router registration
│   ├── api/                             # REST API endpoints
│   │   ├── queries.py                   # Module 1 - User queries
│   │   ├── classification.py            # Module 2 - Issue classification
│   │   ├── tickets.py                   # Module 3 - Ticket management
│   │   ├── agent.py                     # Module 4+6 - AI agent analysis + tool execution
│   │   ├── state.py                     # Module 5 - Agent state management
│   │   ├── memory.py                    # Module 7 - Agent memory
│   │   ├── knowledge.py                 # Module 8 - Knowledge base
│   │   ├── rag.py                       # Module 9 - RAG search
│   │   └── troubleshooting.py           # Module 10 - Multi-step troubleshooting
│   ├── agents/
│   │   ├── helpdesk_agent.py            # Core AI agent
│   │   └── prompts.py                   # Agent prompt templates
│   ├── ai/
│   │   ├── model.py                     # Module 4 - Pretrained model loader
│   │   └── inference.py                 # Module 4 - Inference engine + tool selection
│   ├── state/
│   │   ├── state_manager.py             # Module 5 - State management logic
│   │   ├── state_store.py               # Module 5 - In-memory state storage
│   │   └── transitions.py               # Module 5 - Valid state transitions
│   ├── classifier/
│   │   ├── classifier.py                # Module 2 - Issue classifier
│   │   └── rules.py                     # Module 2 - Classification rules
│   ├── tools/
│   │   ├── base.py                      # Module 6 - BaseTool abstraction
│   │   ├── registry.py                  # Module 6 - Tool registry
│   │   ├── executor.py                  # Module 6 - Tool executor
│   │   ├── network_tools.py             # Module 6 - Network diagnostic tools
│   │   ├── vpn_tools.py                 # Module 6 - VPN tools
│   │   ├── system_tools.py              # Module 6 - System status tools
│   │   └── diagnostic_tools.py          # Module 6 - Diagnostic report tool
│   ├── memory/                          # Module 7 - Agent Memory
│   │   ├── memory_repository.py         # In-memory storage for past issues
│   │   └── memory_manager.py            # Store/retrieve/search memories
│   ├── knowledge/                       # Module 8 - IT Knowledge Base
│   │   └── knowledge_base.py            # 10 IT troubleshooting documents
│   ├── rag/                             # Module 9 - RAG Pipeline
│   │   ├── embeddings.py                # Sentence-transformer embeddings
│   │   ├── vector_store.py              # Local numpy vector store
│   │   ├── retriever.py                 # Document retriever
│   │   └── pipeline.py                  # RAG pipeline (search + context)
│   ├── schemas/                         # Pydantic schemas
│   ├── services/                        # Business logic services
│   ├── models/                          # Data models
│   └── tests/                           # Unit tests
├── scripts/
│   └── ingest_knowledge.py              # Knowledge base seed script
├── requirements.txt
└── README.md
```

## Modules

### Module 1 - User Query
- `POST /api/queries` - Submit user IT problem

### Module 2 - Issue Classification
- `POST /api/classify` - Classify IT issue into category/priority/subcategory

### Module 3 - Ticket Management
- `POST /api/tickets` - Create ticket
- `GET /api/tickets` - List tickets
- `GET /api/tickets/{id}` - Get ticket
- `PATCH /api/tickets/{id}/status` - Update status

### Module 4 - AI Helpdesk Agent
- `POST /api/agent/analyze` - Analyze ticket and return AgentDecision

### Module 5 - Agent State Management
- `POST /api/state/{ticket_id}/initialize` - Initialize agent state
- `GET /api/state/{ticket_id}` - Get current agent state
- `PATCH /api/state/{ticket_id}/stage` - Update workflow stage
- `POST /api/state/{ticket_id}/answer` - Add user answer
- `POST /api/state/{ticket_id}/complete-step` - Complete current step
- `POST /api/state/{ticket_id}/update-decision` - Update agent decision

### Module 6 - Tool Calling and Tool Execution
- `POST /api/agent/execute` - Run AI troubleshooting with tool calling

### Module 7 - Agent Memory
- `POST /api/memory` - Store a memory
- `GET /api/memory` - List all memories
- `GET /api/memory/{ticket_id}` - Get memories for a ticket
- `POST /api/memory/search` - Search relevant memories

### Module 8 - IT Knowledge Base
- `GET /api/knowledge` - List all knowledge documents
- `GET /api/knowledge/{document_id}` - Get a specific document
- `POST /api/knowledge/search` - Search knowledge base

### Module 9 - Retrieval-Augmented Generation (RAG)
- `POST /api/rag/search` - Semantic search with embeddings

### Module 10 - Planning and Multi-Step Troubleshooting
- `POST /api/troubleshooting/start` - Start troubleshooting with memory + RAG + tools
- `POST /api/troubleshooting/continue` - Continue troubleshooting from saved state

## Setup

### Create Virtual Environment

**Windows:**
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Linux / macOS:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Verify venv is active:**
```bash
# Windows
where python
# Should show path ending in ...\backend\venv\Scripts\python.exe

# Linux / macOS
which python
# Should show path ending in .../backend/venv/bin/python
```

### Run the Server

```bash
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000

## Swagger UI

Swagger UI is available at http://localhost:8000/docs

## Unit Tests

```bash
python -m pytest tests/ -v
```

## curl Examples

```bash
# Create ticket
curl -X POST http://localhost:8000/api/tickets \
  -H "Content-Type: application/json" \
  -d "{\"user_query\": \"My VPN is not connecting.\", \"category\": \"VPN\", \"subcategory\": \"VPN Connection\", \"priority\": \"Medium\", \"confidence\": 0.92, \"reason\": \"VPN issue\"}"

# Analyze with AI agent
curl -X POST http://localhost:8000/api/agent/analyze \
  -H "Content-Type: application/json" \
  -d "{\"ticket_id\": \"IT-000001\"}"

# Execute AI troubleshooting
curl -X POST http://localhost:8000/api/agent/execute \
  -H "Content-Type: application/json" \
  -d "{\"ticket_id\": \"IT-000001\"}"

# Start full troubleshooting with memory + RAG + tools
curl -X POST http://localhost:8000/api/troubleshooting/start \
  -H "Content-Type: application/json" \
  -d "{\"ticket_id\": \"IT-000001\", \"query\": \"My VPN is not connecting\"}"

# Search knowledge base
curl -X POST http://localhost:8000/api/knowledge/search \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"VPN connection\", \"limit\": 3}"

# Semantic RAG search
curl -X POST http://localhost:8000/api/rag/search \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"My VPN is not connecting\", \"limit\": 3}"

# Store memory
curl -X POST http://localhost:8000/api/memory \
  -H "Content-Type: application/json" \
  -d "{\"ticket_id\": \"IT-001\", \"issue_summary\": \"VPN not connecting\", \"category\": \"VPN\", \"solution\": \"Restart VPN client\", \"outcome\": \"Resolved\"}"

# Search memories
curl -X POST http://localhost:8000/api/memory/search \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"VPN connection issue\", \"top_k\": 3}"
```
