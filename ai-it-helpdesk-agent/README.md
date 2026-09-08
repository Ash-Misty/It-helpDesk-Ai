# AI IT Helpdesk Agent

Modular AI IT Helpdesk application with intelligent ticket analysis, agent state management, and tool calling.

## Architecture

```
ai-it-helpdesk-agent/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── queries.py
│   │   │   ├── classification.py
│   │   │   ├── tickets.py
│   │   │   ├── agent.py
│   │   │   └── state.py
│   │   ├── agents/
│   │   │   ├── helpdesk_agent.py
│   │   │   └── prompts.py
│   │   ├── ai/
│   │   │   ├── model.py
│   │   │   └── inference.py
│   │   ├── state/
│   │   │   ├── __init__.py
│   │   │   ├── state_manager.py
│   │   │   ├── state_store.py
│   │   │   └── transitions.py
│   │   ├── classifier/
│   │   │   ├── __init__.py
│   │   │   ├── rules.py
│   │   │   └── classifier.py
│   │   ├── models/
│   │   │   └── ticket.py
│   │   ├── schemas/
│   │   │   ├── query.py
│   │   │   ├── classification.py
│   │   │   ├── ticket.py
│   │   │   ├── agent.py
│   │   │   └── state.py
│   │   ├── services/
│   │   │   ├── query_service.py
│   │   │   ├── classification_service.py
│   │   │   ├── ticket_service.py
│   │   │   └── state_service.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── registry.py
│   │   │   ├── executor.py
│   │   │   ├── network_tools.py
│   │   │   ├── vpn_tools.py
│   │   │   ├── system_tools.py
│   │   │   └── diagnostic_tools.py
│   │   └── tests/
│   │       ├── test_state.py
│   │       ├── test_tools.py
│   │       └── test_agent_execution.py
│   ├── requirements.txt
│   ├── README.md
│   └── venv/
├── frontend/
│   └── src/
│       ├── components/
│       │   └── ChatWindow.jsx
│       ├── services/
│       │   └── api.js
│       ├── App.jsx
│       ├── main.jsx
│       └── index.css
└── README.md
```

## Modules

### Module 1 - User Query
- POST /api/queries - Submit user IT problem via chat interface

### Module 2 - Issue Classification
- POST /api/classify - Classify IT issue into category/priority/subcategory

### Module 3 - Ticket Management
- POST /api/tickets - Create ticket
- GET /api/tickets - List tickets
- GET /api/tickets/{id} - Get ticket
- PATCH /api/tickets/{id}/status - Update status

### Module 4 - AI Helpdesk Agent
- POST /api/agent/analyze - Analyze ticket and return AgentDecision

### Module 5 - Agent State Management
- POST /api/state/{ticket_id}/initialize - Initialize agent state
- GET /api/state/{ticket_id} - Get current agent state
- PATCH /api/state/{ticket_id}/stage - Update workflow stage
- POST /api/state/{ticket_id}/answer - Add user answer
- POST /api/state/{ticket_id}/complete-step - Complete current step

### Module 6 - Tool Calling and Tool Execution
- POST /api/agent/execute - Run AI troubleshooting with tool calling

## Module 6 - Tool Calling and Tool Execution

### What is Tool Calling in Agentic AI?

Tool Calling allows an AI Agent to interact with external systems in a controlled, safe manner. Instead of simply generating text, the Agent can:

1. Read the current ticket and agent state
2. Decide whether a tool is required
3. Select an appropriate registered tool
4. Generate valid tool arguments
5. Execute the tool through a controlled executor
6. Receive the tool result
7. Store the result in Agent State
8. Re-evaluate the situation
9. Decide what should happen next

This creates a genuine Agentic AI loop:

Agent
  ↓
Analyze State
  ↓
Decide Action
  ↓
Select Tool
  ↓
Execute Tool
  ↓
Tool Result
  ↓
Update State
  ↓
Agent Re-evaluates
  ↓
Next Action

### Why Tools Are Needed

Without tools, an AI Agent can only provide text-based advice. With tools, the Agent can:

- Gather diagnostic information (check internet, VPN, system status)
- Make context-aware decisions based on real diagnostic data
- Build a troubleshooting history
- Recommend solutions based on evidence
- Escalate appropriately when tools indicate serious issues

### Available Tools

All tools are simulated and read-only for demonstration purposes. They do NOT access real systems.

| Tool | Description | Arguments |
|------|-------------|-----------|
| check_internet_connection | Checks internet connectivity | None |
| check_dns_status | Checks DNS resolution for a domain | domain (string, required) |
| check_vpn_status | Checks VPN connection status | None |
| check_system_status | Checks OS, uptime, CPU, memory | None |
| check_disk_space | Checks available disk space | None |
| check_application_status | Checks if an application is running | application (string, required) |
| create_diagnostic_report | Generates a diagnostic summary | None |

### Tool Registry

The ToolRegistry (app/tools/registry.py) is the central registry for all tools. It:

- Stores all registered tools by name
- Validates that only registered tools can be executed
- Provides tool metadata (description, input schema, safety flags)
- Prevents arbitrary function execution

No tool can execute unless it is registered in the ToolRegistry.

### Tool Executor

The ToolExecutor (app/tools/executor.py) is responsible for:

1. Receiving a tool name and arguments
2. Verifying the tool exists in the registry
3. Validating arguments against the tool's input schema
4. Executing the tool with a timeout (30 seconds)
5. Catching errors and returning structured results
6. Recording execution metadata (timing, simulated flag)

### Tool Validation

Every tool has a defined input_schema using JSON Schema format. The BaseTool.validate_arguments() method checks:

- Required fields are present
- No unknown/extra fields are passed
- Field types match the schema
- String length constraints are respected
- Numeric ranges are respected

Example: check_dns_status requires a domain string (1-255 characters). Passing no arguments or a non-string value returns a validation error before the tool executes.

### Agent Tool Selection

The Agent uses the InferenceEngine to decide which tool to use. The decision process:

1. Receives: user query, ticket, current state, available tools, previous tool results
2. Checks for security/critical issues → escalates immediately
3. Checks for unanswered questions → asks for information
4. Selects context-appropriate tools based on the issue type:
   - VPN/Network issues → check_internet_connection → check_vpn_status
   - DNS issues → check_dns_status
   - Printer issues → check_application_status
5. Falls back to general diagnostic tools
6. Returns structured ToolDecision

### Structured Tool Decision

The model returns structured output:

{
  "action": "call_tool",
  "tool_name": "check_vpn_status",
  "arguments": {},
  "reason": "The ticket involves a VPN connection issue."
}

Valid actions:
- call_tool - Execute a tool
- ask_information - Request user input
- recommend_solution - Provide a recommendation
- escalate - Escalate to human technician
- resolve - Mark issue as resolved
- no_action - No action needed

### Tool Result → State

After a tool executes, its result is stored in Agent State:

{
  "tool_calls": [
    {
      "tool_name": "check_internet_connection",
      "arguments": {},
      "timestamp": "2026-09-08T06:43:03.618032"
    }
  ],
  "tool_results": [
    {
      "tool_name": "check_internet_connection",
      "success": true,
      "result": {"connected": true, "latency_ms": 42},
      "error": null,
      "execution_time_ms": 15.0,
      "simulated": true,
      "timestamp": "2026-09-08T06:43:03.618032"
    }
  ]
}

Previous tool results are never overwritten. A complete history is maintained.

### Agent Execution Loop

The AgentExecutionService (app/services/agent_execution_service.py) implements the controlled loop:

1. Load ticket and state (auto-initialize if needed)
2. Loop (max 5 iterations):
   a. Get current agent context from state
   b. Ask Agent for next action
   c. If call_tool: execute tool, record result, update state
   d. If ask_information: update stage, break
   e. If escalate: update stage, break
   f. If recommend_solution: update stage, break
   g. If resolve: update stage, break
   h. If no_action: break
3. Return all actions and final state

### Maximum Tool-Call Safety Limit

The loop has a hard limit of MAX_TOOL_CALLS = 5. If reached, execution stops safely and returns:

{
  "status": "max_tool_calls_reached"
}

The Agent never executes tools indefinitely.

### API Endpoint

#### POST /api/agent/execute

Request:
{
  "ticket_id": "IT-000001"
}

Response:
{
  "success": true,
  "ticket_id": "IT-000001",
  "status": "in_progress",
  "actions": [
    {
      "type": "tool_call",
      "tool": "check_internet_connection",
      "arguments": {},
      "reason": "Checking internet connection first."
    },
    {
      "type": "tool_result",
      "tool": "check_internet_connection",
      "success": true,
      "result": {"connected": true, "latency_ms": 42}
    },
    {
      "type": "tool_call",
      "tool": "check_vpn_status"
    }
  ],
  "next_action": "ask_information",
  "state": { ... }
}

### Example Execution

User: "My VPN is not connecting."

1. Agent reads ticket: VPN/VPN Connection/Medium
2. Agent decides: call_tool → check_internet_connection
3. Tool executes: connected: true, latency_ms: 42
4. State updated with tool result
5. Agent re-evaluates: internet is fine, check VPN
6. Agent decides: call_tool → check_vpn_status
7. Tool executes: connected: false, status: connection_failed
8. State updated with tool result
9. Agent re-evaluates: VPN is the issue
10. Agent decides: ask_information → "Are you receiving an authentication error?"
11. Loop stops, returns all actions

### State Integration

Module 6 extends Module 5's AgentState with:

- tool_calls: List[ToolCall] - Record of all tool invocations
- tool_results: List[ToolResultRecord] - Record of all tool results

The StateManager provides:
- record_tool_call(ticket_id, tool_name, arguments) - Log a tool invocation
- record_tool_result(ticket_id, tool_name, success, result, ...) - Log a tool result
- get_agent_context(ticket_id) - Returns full context including tool history

### Tool History

Every tool call is recorded with:
- Tool name
- Arguments passed
- Success/failure status
- Result data
- Error message (if failed)
- Execution time
- Simulated flag
- Timestamp

This history supports:
- Agent Memory (future module)
- Troubleshooting
- Root Cause Analysis
- Technician Handoff
- Audit Logs

### Error Handling

The system handles:

1. Unknown tool → Returns controlled error, does not execute
2. Invalid arguments → Validated before execution, returns error
3. Tool execution failure → Caught, recorded in state, Agent decides next step
4. Model returning invalid tool name → Agent layer falls back to no_action
5. Model returning malformed JSON → Inference engine falls back to rule-based decision
6. Missing ticket → Returns 404
7. Missing Agent State → Auto-initializes from ticket
8. Model unavailable → Falls back to rule-based inference
9. Tool timeout → Returns timeout error after 30 seconds
10. Maximum tool-call limit → Stops safely, returns max_tool_calls_reached

### Security Restrictions

NEVER allow the LLM to:
- Execute arbitrary shell commands
- Execute arbitrary Python code
- Access arbitrary files
- Access passwords or credentials
- Modify system configuration
- Disable security controls
- Perform destructive actions

Only registered tools may execute. Tool names are validated against the registry. Arguments are validated against tool schemas. The LLM never directly executes code.

### Frontend

The React UI has been updated with:

1. "Run AI Troubleshooting" button - Appears after agent analysis
2. Agent Activity Panel - Shows the complete execution log:
   - Tool calls with arguments
   - Tool results (success/failure)
   - Agent asking for information
   - Escalation warnings
   - Solution recommendations
   - Maximum call limit warnings
3. Tool History - Shows all tool calls in the state card with status, timing, and simulated flag

### venv Setup

Windows:
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

Linux/macOS:
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Verify venv is active:
# Windows
where python
# Should show: ...\backend\venv\Scripts\python.exe

# Linux/macOS
which python
# Should show: .../backend/venv/bin/python

### Testing

### Unit Tests
cd backend
venv\Scripts\python -m pytest tests/ -v

Test coverage (91 tests total):
- Tool registration and discovery
- Valid tool execution
- Unknown tool handling
- Invalid arguments (missing, wrong type, too long, unknown fields)
- Tool failure handling
- Tool decision schema validation
- Agent tool selection (VPN, Internet, Printer, Security, Critical)
- Maximum tool call limit
- State updates after tool execution
- Tool history preservation
- Missing ticket/state handling
- Malformed model output fallback
- Error handling

### curl Examples

# Execute agent troubleshooting
curl -X POST http://localhost:8000/api/agent/execute \
  -H "Content-Type: application/json" \
  -d '{"ticket_id": "IT-000001"}'

### Frontend Testing
1. Open http://localhost:5173
2. Type an IT problem and submit
3. Verify classification card appears
4. Verify ticket card appears
5. Click "Analyze with AI Agent"
6. Verify agent decision card appears
7. Click "Run AI Troubleshooting"
8. Verify Agent Activity panel shows tool calls and results
9. Verify tool history appears in state card
10. Submit an answer to a question if prompted

### Swagger UI
Available at http://localhost:8000/docs

## Complete Module 1-6 Flow

USER
  ↓
MODULE 1 - User Query
  POST /api/queries
  ↓
MODULE 2 - Issue Classification
  POST /api/classify
  ↓
MODULE 3 - Ticket Creation
  POST /api/tickets
  ↓
MODULE 4 - AI Helpdesk Agent
  POST /api/agent/analyze
  ↓
Agent Decision
  ↓
MODULE 5 - Agent State Created
  POST /api/state/{ticket_id}/initialize
  ↓
State stored in memory
  ↓
Agent reads current state context
  ↓
Workflow progresses:
  - Stages: created → analyzing → planning → troubleshooting → verifying → resolved
  - Questions asked ↔ User answers received
  - Steps completed one at a time
  - Invalid transitions rejected
  ↓
MODULE 6 - Tool Calling
  POST /api/agent/execute
  ↓
Agent selects tool based on context
  ↓
Tool Registry validates tool name
  ↓
Tool Executor validates arguments
  ↓
Tool executes (simulated/read-only)
  ↓
Tool Result stored in Agent State
  ↓
Agent re-evaluates with new data
  ↓
Next Action (tool, ask, escalate, resolve)
  ↓
READY FOR NEXT AGENTIC AI MODULE

## Future Development

**State vs Memory (clear distinction):**
- **State** (Module 5): Short-term working context for a single ticket workflow
- **Memory** (future module): Long-term user history, preferences, past tickets

**Storage upgrade path:**
- Current: In-memory with threading lock
- Future: Replace InMemoryStateStore with Redis/PostgreSQL/MongoDB

**Agent integration path:**
- Agent reads `get_agent_context(ticket_id)` to get current state
- Agent decision updates state via `update_agent_decision`
- Tool calling via `AgentExecutionService.execute()`
- Future modules will add RAG, autonomous workflows, and memory

## Not Yet Implemented (Future Modules)

- Long-term Memory
- RAG / Knowledge Base
- Multi-step Troubleshooting Engine
- Root Cause Analysis
- Autonomous Escalation Workflow
- Technician Handoff
- Database persistence
- Admin Dashboard
