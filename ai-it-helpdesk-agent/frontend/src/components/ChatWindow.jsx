import { useState, useRef, useEffect } from "react";
import {
  postQuery,
  checkHealth,
  classifyQuery,
  createTicket,
  analyzeTicket,
  initializeState,
  addAnswer,
  completeStep,
  executeAgent,
} from "../services/api";

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendUp, setBackendUp] = useState(true);
  const [classification, setClassification] = useState(null);
  const [ticket, setTicket] = useState(null);
  const [agentDecision, setAgentDecision] = useState(null);
  const [agentState, setAgentState] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [initializing, setInitializing] = useState(false);
  const [answerInput, setAnswerInput] = useState("");
  const [submittingAnswer, setSubmittingAnswer] = useState(false);
  const [completingStep, setCompletingStep] = useState(false);
  const [troubleshooting, setTroubleshooting] = useState(false);
  const [troubleshootResult, setTroubleshootResult] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    checkHealth()
      .then(() => setBackendUp(true))
      .catch(() => setBackendUp(false));
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, classification, ticket, agentDecision, agentState, troubleshootResult]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");
    setLoading(true);
    setError(null);
    setClassification(null);
    setTicket(null);
    setAgentDecision(null);
    setAgentState(null);
    setTroubleshooting(false);
    setTroubleshootResult(null);

    try {
      await postQuery(trimmed);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Your IT helpdesk request has been received. AI diagnosis will be added in the next module.",
        },
      ]);

      const classResult = await classifyQuery(trimmed);
      setClassification(classResult);

      const ticketResult = await createTicket({
        user_query: trimmed,
        category: classResult.category,
        subcategory: classResult.subcategory,
        priority: classResult.priority,
        confidence: classResult.confidence,
        reason: classResult.reason,
      });
      setTicket(ticketResult.ticket);
    } catch (err) {
      setError(
        "Unable to connect to the IT Helpdesk server. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!ticket || analyzing) return;
    setAnalyzing(true);
    setAgentDecision(null);
    setError(null);

    try {
      const result = await analyzeTicket(ticket.ticket_id);
      setAgentDecision(result.agent_decision);

      const stateResult = await initializeState(ticket.ticket_id);
      setAgentState(stateResult.state);
    } catch (err) {
      setError(
        "Unable to connect to the IT Helpdesk server. Please try again."
      );
    } finally {
      setAnalyzing(false);
    }
  };

  const handleRunTroubleshooting = async () => {
    if (!ticket || troubleshooting) return;
    setTroubleshooting(true);
    setTroubleshootResult(null);
    setError(null);

    try {
      const result = await executeAgent(ticket.ticket_id);
      setTroubleshootResult(result);

      if (result.state) {
        setAgentState(result.state);
      }
    } catch (err) {
      setError(
        "Unable to run AI troubleshooting. Please try again."
      );
    } finally {
      setTroubleshooting(false);
    }
  };

  const handleAnswer = async () => {
    if (!agentState || !answerInput.trim() || submittingAnswer) return;
    const firstUnansweredQuestion = (agentState.questions_asked || [])
      .filter(
        (q) =>
          !(agentState.user_answers || []).some((a) => a.question === q)
      )
      .shift();

    setSubmittingAnswer(true);
    setError(null);

    try {
      const result = await addAnswer(
        ticket.ticket_id,
        firstUnansweredQuestion || "User input",
        answerInput.trim()
      );
      setAgentState(result.state);
      setAnswerInput("");
    } catch (err) {
      setError(
        "Unable to submit your answer. Please try again."
      );
    } finally {
      setSubmittingAnswer(false);
    }
  };

  const handleCompleteStep = async () => {
    if (!agentState || completingStep) return;
    setCompletingStep(true);
    setError(null);

    try {
      const result = await completeStep(ticket.ticket_id);
      setAgentState(result.state);
    } catch (err) {
      setError(
        "Unable to complete step. Please try again."
      );
    } finally {
      setCompletingStep(false);
    }
  };

  const unansweredQuestions = agentState
    ? (agentState.questions_asked || []).filter(
        (q) => !(agentState.user_answers || []).some((a) => a.question === q)
      )
    : [];

  const renderActivityItem = (action, index) => {
    const key = `activity-${index}`;
    switch (action.type) {
      case "tool_call":
        return (
          <div key={key} className="activity-item tool-call">
            <div className="activity-icon">🔧</div>
            <div className="activity-content">
              <div className="activity-title">Tool: {action.tool}</div>
              {action.arguments && Object.keys(action.arguments).length > 0 && (
                <div className="activity-detail">
                  Arguments: {JSON.stringify(action.arguments)}
                </div>
              )}
              {action.reason && (
                <div className="activity-detail">{action.reason}</div>
              )}
            </div>
          </div>
        );
      case "tool_result":
        return (
          <div key={key} className="activity-item tool-result">
            <div className="activity-icon">📋</div>
            <div className="activity-content">
              <div className="activity-title">
                Result: {action.success ? "Success" : "Failed"}
              </div>
              {action.error && (
                <div className="activity-detail error-text">{action.error}</div>
              )}
              {action.result && (
                <div className="activity-detail">
                  {JSON.stringify(action.result)}
                </div>
              )}
            </div>
          </div>
        );
      case "tool_error":
        return (
          <div key={key} className="activity-item tool-error">
            <div className="activity-icon">⚠️</div>
            <div className="activity-content">
              <div className="activity-title">Tool Error</div>
              <div className="activity-detail error-text">{action.error}</div>
            </div>
          </div>
        );
      case "ask_information":
        return (
          <div key={key} className="activity-item ask-info">
            <div className="activity-icon">💬</div>
            <div className="activity-content">
              <div className="activity-title">Agent: Additional information required</div>
              {action.reason && (
                <div className="activity-detail">{action.reason}</div>
              )}
            </div>
          </div>
        );
      case "escalate":
        return (
          <div key={key} className="activity-item escalate">
            <div className="activity-icon">🔴</div>
            <div className="activity-content">
              <div className="activity-title">Agent: Escalation recommended</div>
              {action.reason && (
                <div className="activity-detail">{action.reason}</div>
              )}
            </div>
          </div>
        );
      case "recommend_solution":
        return (
          <div key={key} className="activity-item recommend">
            <div className="activity-icon">✅</div>
            <div className="activity-content">
              <div className="activity-title">Agent: Solution recommended</div>
              {action.reason && (
                <div className="activity-detail">{action.reason}</div>
              )}
            </div>
          </div>
        );
      case "resolve":
        return (
          <div key={key} className="activity-item resolve">
            <div className="activity-icon">🎉</div>
            <div className="activity-content">
              <div className="activity-title">Agent: Issue resolved</div>
              {action.reason && (
                <div className="activity-detail">{action.reason}</div>
              )}
            </div>
          </div>
        );
      case "no_action":
        return (
          <div key={key} className="activity-item no-action">
            <div className="activity-icon">⏸️</div>
            <div className="activity-content">
              <div className="activity-title">Agent: No action</div>
              {action.reason && (
                <div className="activity-detail">{action.reason}</div>
              )}
            </div>
          </div>
        );
      case "max_calls_reached":
        return (
          <div key={key} className="activity-item max-calls">
            <div className="activity-icon">🛑</div>
            <div className="activity-content">
              <div className="activity-title">Limit Reached</div>
              {action.reason && (
                <div className="activity-detail">{action.reason}</div>
              )}
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>AI IT Helpdesk</h1>
        <p>Describe your IT problem and our AI helpdesk will assist you.</p>
      </header>

      <div className="messages-area">
        {!backendUp && (
          <div className="error-banner">
            Unable to connect to the IT Helpdesk server. Please try again.
          </div>
        )}

        {messages.length === 0 && !loading && (
          <div className="empty-state">
            <p>No conversation yet</p>
            <p>Describe your problem below.</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`message ${msg.role === "user" ? "user" : "assistant"}`}
          >
            <div className="message-bubble">{msg.content}</div>
          </div>
        ))}

        {classification && (
          <div className="classification-card">
            <h3>Classification Result</h3>
            <div className="classification-grid">
              <div className="classification-item">
                <span className="label">Category</span>
                <span className="value">{classification.category}</span>
              </div>
              <div className="classification-item">
                <span className="label">Subcategory</span>
                <span className="value">{classification.subcategory}</span>
              </div>
              <div className="classification-item">
                <span className="label">Priority</span>
                <span className={`value priority-${classification.priority.toLowerCase()}`}>
                  {classification.priority}
                </span>
              </div>
              <div className="classification-item">
                <span className="label">Confidence</span>
                <span className="value">
                  {Math.round(classification.confidence * 100)}%
                </span>
              </div>
            </div>
            <p className="classification-reason">{classification.reason}</p>
          </div>
        )}

        {ticket && (
          <div className="ticket-card">
            <h3>IT Helpdesk Ticket Created</h3>
            <div className="ticket-grid">
              <div className="ticket-item">
                <span className="label">Ticket ID</span>
                <span className="value">{ticket.ticket_id}</span>
              </div>
              <div className="ticket-item">
                <span className="label">Issue</span>
                <span className="value">{ticket.user_query}</span>
              </div>
              <div className="ticket-item">
                <span className="label">Category</span>
                <span className="value">{ticket.category}</span>
              </div>
              <div className="ticket-item">
                <span className="label">Subcategory</span>
                <span className="value">{ticket.subcategory}</span>
              </div>
              <div className="ticket-item">
                <span className="label">Priority</span>
                <span className={`value priority-${ticket.priority.toLowerCase()}`}>
                  {ticket.priority}
                </span>
              </div>
              <div className="ticket-item">
                <span className="label">Status</span>
                <span className="value">{ticket.status}</span>
              </div>
              <div className="ticket-item">
                <span className="label">Confidence</span>
                <span className="value">{Math.round(ticket.confidence * 100)}%</span>
              </div>
            </div>
          </div>
        )}

        {ticket && !agentDecision && !troubleshootResult && (
          <div className="message assistant">
            <div className="message-bubble">
              <div className="button-group">
                <button
                  className="analyze-button"
                  onClick={handleAnalyze}
                  disabled={analyzing || !backendUp}
                >
                  {analyzing ? "Analyzing..." : "Analyze with AI Agent"}
                </button>
              </div>
            </div>
          </div>
        )}

        {agentDecision && !troubleshootResult && (
          <div className="agent-card">
            <h3>AI Agent Analysis</h3>
            <div className="agent-grid">
              <div className="agent-item">
                <span className="label">Understanding</span>
                <span className="value">{agentDecision.understanding}</span>
              </div>
              <div className="agent-item">
                <span className="label">Problem Type</span>
                <span className="value">{agentDecision.problem_type}</span>
              </div>
              <div className="agent-item">
                <span className="label">Next Action</span>
                <span className={`value action-${agentDecision.next_action}`}>
                  {agentDecision.next_action.replace(/_/g, " ")}
                </span>
              </div>
              <div className="agent-item">
                <span className="label">More Information Required</span>
                <span className={`value ${agentDecision.requires_more_information ? "text-yes" : "text-no"}`}>
                  {agentDecision.requires_more_information ? "Yes" : "No"}
                </span>
              </div>
              <div className="agent-item">
                <span className="label">Auto Resolve</span>
                <span className={`value ${agentDecision.can_auto_resolve ? "text-yes" : "text-no"}`}>
                  {agentDecision.can_auto_resolve ? "Yes" : "No"}
                </span>
              </div>
              <div className="agent-item">
                <span className="label">Escalation Required</span>
                <span className={`value ${agentDecision.should_escalate ? "text-yes" : "text-no"}`}>
                  {agentDecision.should_escalate ? "Yes" : "No"}
                </span>
              </div>
            </div>

            {agentDecision.questions && agentDecision.questions.length > 0 && (
              <div className="agent-section">
                <h4>Questions</h4>
                <ul className="agent-list">
                  {agentDecision.questions.map((q, idx) => (
                    <li key={idx}>{q}</li>
                  ))}
                </ul>
              </div>
            )}

            {agentDecision.initial_plan && agentDecision.initial_plan.length > 0 && (
              <div className="agent-section">
                <h4>Initial Troubleshooting Plan</h4>
                <ol className="agent-list ordered">
                  {agentDecision.initial_plan.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </div>
            )}

            <p className="agent-reason">{agentDecision.reason}</p>

            <div className="agent-section">
              <button
                className="troubleshoot-button"
                onClick={handleRunTroubleshooting}
                disabled={troubleshooting || !backendUp}
              >
                {troubleshooting ? "Running AI Troubleshooting..." : "Run AI Troubleshooting"}
              </button>
            </div>
          </div>
        )}

        {troubleshootResult && (
          <div className="agent-card">
            <h3>AI Agent Activity</h3>

            {troubleshootResult.actions && troubleshootResult.actions.length > 0 && (
              <div className="activity-panel">
                <div className="activity-header">
                  Agent execution log ({troubleshootResult.actions.length} actions)
                </div>
                <div className="activity-list">
                  {troubleshootResult.actions.map((action, idx) =>
                    renderActivityItem(action, idx)
                  )}
                </div>
              </div>
            )}

            <div className="agent-section">
              <div className="status-row">
                <span className="status-label">Status:</span>
                <span className={`status-value status-${troubleshootResult.status}`}>
                  {troubleshootResult.status.replace(/_/g, " ")}
                </span>
              </div>
              <div className="status-row">
                <span className="status-label">Next Action:</span>
                <span className="status-value">
                  {troubleshootResult.next_action.replace(/_/g, " ")}
                </span>
              </div>
            </div>

            {troubleshootResult.status === "requires_user_input" && (
              <div className="agent-section info-box">
                <strong>Additional information required.</strong>
                <p>The agent needs more information before it can continue troubleshooting.</p>
              </div>
            )}

            {troubleshootResult.status === "escalated" && (
              <div className="agent-section warning-box">
                <strong>Escalation recommended.</strong>
                <p>This issue requires human technician attention.</p>
              </div>
            )}

            {troubleshootResult.status === "solution_recommended" && (
              <div className="agent-section success-box">
                <strong>Solution recommended.</strong>
                <p>The agent has gathered enough diagnostic information to provide a recommendation.</p>
              </div>
            )}

            {troubleshootResult.status === "max_tool_calls_reached" && (
              <div className="agent-section warning-box">
                <strong>Maximum tool calls reached.</strong>
                <p>The agent has performed the maximum allowed diagnostic steps. Review the results above.</p>
              </div>
            )}

            {troubleshootResult.status === "completed" && (
              <div className="agent-section success-box">
                <strong>Issue resolved.</strong>
                <p>The agent has marked this issue as resolved.</p>
              </div>
            )}
          </div>
        )}

        {agentState && (
          <div className="state-card">
            <h3>AI Agent Workflow State</h3>
            <div className="state-grid">
              <div className="state-item">
                <span className="label">Ticket ID</span>
                <span className="value">{agentState.ticket_id}</span>
              </div>
              <div className="state-item">
                <span className="label">Current Stage</span>
                <span className="value stage-badge">{agentState.current_stage}</span>
              </div>
              <div className="state-item">
                <span className="label">Status</span>
                <span className={`value status-badge status-${agentState.status}`}>
                  {agentState.status}
                </span>
              </div>
              <div className="state-item">
                <span className="label">Current Step</span>
                <span className="value">
                  {agentState.current_step_index + 1} of {agentState.current_plan.length}
                </span>
              </div>
              <div className="state-item">
                <span className="label">Completed Steps</span>
                <span className="value">{agentState.completed_steps.length}</span>
              </div>
              <div className="state-item">
                <span className="label">Last Action</span>
                <span className="value">{agentState.last_action || "N/A"}</span>
              </div>
            </div>

            {agentState.tool_results && agentState.tool_results.length > 0 && (
              <div className="agent-section">
                <h4>Tool History ({agentState.tool_results.length} calls)</h4>
                <div className="tool-history-list">
                  {agentState.tool_results.map((tr, idx) => (
                    <div key={idx} className="tool-history-item">
                      <span className="tool-history-name">{tr.tool_name}</span>
                      <span className={`tool-history-status ${tr.success ? "success" : "failure"}`}>
                        {tr.success ? "OK" : "FAIL"}
                      </span>
                      {tr.execution_time_ms !== undefined && (
                        <span className="tool-history-time">{tr.execution_time_ms.toFixed(1)}ms</span>
                      )}
                      {tr.simulated && <span className="tool-history-sim">SIM</span>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {agentState.current_plan && agentState.current_plan.length > 0 && (
              <div className="agent-section">
                <h4>Current Plan</h4>
                <ol className="agent-list ordered">
                  {agentState.current_plan.map((step, idx) => (
                    <li
                      key={idx}
                      className={
                        idx < agentState.current_step_index
                          ? "step-completed"
                          : idx === agentState.current_step_index
                          ? "step-current"
                          : ""
                      }
                    >
                      {step}
                      {idx === agentState.current_step_index && (
                        <span className="step-badge">Current</span>
                      )}
                      {agentState.completed_steps.includes(step) &&
                        idx !== agentState.current_step_index && (
                          <span className="step-badge done">Done</span>
                        )}
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {unansweredQuestions.length > 0 && (
              <div className="agent-section">
                <h4>Pending Questions</h4>
                <ul className="agent-list">
                  {unansweredQuestions.map((q, idx) => (
                    <li key={idx}>{q}</li>
                  ))}
                </ul>
                <div className="answer-form">
                  <input
                    type="text"
                    value={answerInput}
                    onChange={(e) => setAnswerInput(e.target.value)}
                    placeholder="Type your answer..."
                    disabled={submittingAnswer || !backendUp}
                  />
                  <button
                    className="submit-answer-button"
                    onClick={handleAnswer}
                    disabled={submittingAnswer || !answerInput.trim() || !backendUp}
                  >
                    {submittingAnswer ? "Submitting..." : "Submit Answer"}
                  </button>
                </div>
              </div>
            )}

            {agentState.last_action === "agent_analysis" &&
              agentState.completed_steps.length === 0 &&
              agentState.current_plan.length > 0 &&
              unansweredQuestions.length === 0 && (
                <div className="agent-section">
                  <button
                    className="complete-step-button"
                    onClick={handleCompleteStep}
                    disabled={completingStep || !backendUp}
                  >
                    {completingStep ? "Completing..." : "Complete Current Step"}
                  </button>
                </div>
              )}

            <p className="agent-reason">Status: {agentState.status}. Updated: {agentState.updated_at}</p>
          </div>
        )}

        {error && <div className="error-banner">{error}</div>}

        <div ref={messagesEndRef} />
      </div>

      <form className="input-area" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your IT problem..."
          disabled={loading || !backendUp}
        />
        <button type="submit" disabled={loading || !backendUp || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
