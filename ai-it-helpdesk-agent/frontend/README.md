# AI IT Helpdesk Agent - Frontend

React frontend for the AI IT Helpdesk application. Provides a chat interface for submitting IT issues, viewing classification results, creating tickets, analyzing with AI, and running AI-powered troubleshooting.

## Tech Stack

- React 18
- Vite
- Vanilla CSS (no framework)

## Setup

```bash
npm install
npm run dev
```

Frontend runs at http://localhost:5173

## Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |

## Prerequisites

Backend must be running at http://localhost:8000 before starting the frontend.

```bash
cd ../backend
uvicorn app.main:app --reload
```

## Usage Flow

1. Open http://localhost:5173
2. Type an IT problem in the chat input (e.g., "My VPN is not connecting.")
3. Click **Send**
4. View the **Classification Result** card (category, subcategory, priority, confidence)
5. View the **Ticket Created** card with your ticket ID
6. Click **"Analyze with AI Agent"** to run AI analysis
7. View the **AI Agent Analysis** card with understanding, problem type, plan, and questions
8. Click **"Run AI Troubleshooting"** to start the multi-step agent workflow
9. View the **AI Agent Activity** panel showing:
   - Retrieved knowledge documents
   - Relevant past memories
   - Tool calls and results
   - Agent decisions and next actions
10. Answer questions if prompted
11. Complete troubleshooting steps as they appear

## Features

### User Query (Module 1)
- Chat interface for submitting IT problems
- Backend health check indicator

### Issue Classification (Module 2)
- Automatic classification into category/subcategory/priority
- Confidence score and reasoning displayed

### Ticket Management (Module 3)
- Automatic ticket creation after classification
- Ticket ID, status, and details displayed

### AI Agent Analysis (Module 4)
- "Analyze with AI Agent" button
- Displays agent understanding, problem type, and initial plan
- Shows whether more information is needed

### Agent State (Module 5)
- Workflow state card showing current stage, plan, and progress
- Completed steps tracker
- Pending questions with answer input
- "Complete Current Step" button

### Tool Calling (Module 6)
- "Run AI Troubleshooting" button
- Agent Activity panel with tool execution log
- Tool results with success/failure status
- Execution timing and simulated flags

### Agent Memory (Module 7)
- Relevant past memories retrieved automatically
- Displayed in troubleshooting context

### Knowledge Base (Module 8)
- 10 IT troubleshooting documents across 8 categories
- Automatically retrieved based on issue category

### RAG (Module 9)
- Semantic search using sentence-transformers
- Relevant knowledge documents shown in activity panel

### Multi-Step Troubleshooting (Module 10)
- Adaptive agent loop with memory + RAG + tools
- Maximum iteration safety limit
- Continue button for resuming paused troubleshooting

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── ChatWindow.jsx          # Main chat + troubleshooting UI
│   ├── services/
│   │   └── api.js                  # API client functions
│   ├── App.jsx                     # App root
│   ├── main.jsx                    # React entry point
│   └── index.css                   # All styles
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## API Client

The `src/services/api.js` file provides all API functions:

- `postQuery(message)` - Submit user query
- `checkHealth()` - Check backend health
- `classifyQuery(message)` - Classify issue
- `createTicket(data)` - Create ticket
- `analyzeTicket(ticketId)` - Run AI analysis
- `initializeState(ticketId)` - Initialize agent state
- `addAnswer(ticketId, question, answer)` - Submit answer
- `completeStep(ticketId)` - Complete current step
- `executeAgent(ticketId)` - Run AI troubleshooting with tools
