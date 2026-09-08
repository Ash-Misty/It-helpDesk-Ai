# AI IT Helpdesk Agent - Backend

FastAPI backend for the AI IT Helpdesk application with AI-powered agent capabilities.

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

## Endpoints

### Module 1 - User Query
- `GET /api/health` - Health check
- `POST /api/queries` - Submit a user query

### Module 2 - Issue Classification
- `POST /api/classify` - Classify an IT issue

### Module 3 - Ticket Management
- `POST /api/tickets` - Create a ticket
- `GET /api/tickets` - List all tickets
- `GET /api/tickets/{ticket_id}` - Get a specific ticket
- `PATCH /api/tickets/{ticket_id}/status` - Update ticket status

### Module 4 - AI Helpdesk Agent
- `POST /api/agent/analyze` - Analyze a ticket with AI agent

### Module 5 - Agent State Management
- `POST /api/state/{ticket_id}/initialize` - Initialize agent state
- `GET /api/state/{ticket_id}` - Get current agent state
- `PATCH /api/state/{ticket_id}/stage` - Update workflow stage
- `POST /api/state/{ticket_id}/answer` - Add user answer to a question
- `POST /api/state/{ticket_id}/complete-step` - Mark current step as complete
- `POST /api/state/{ticket_id}/update-decision` - Update agent decision in state

## Swagger UI

Swagger UI is available at http://localhost:8000/docs

## Unit Tests

```bash
python -m pytest tests/ -v
```
