import { FormEvent, useEffect, useMemo, useState } from "react";

import { getWorkflow, listWorkflows, submitMessage } from "./api";
import type {
  AttachmentMetadata,
  MessageSubmissionResponse,
  WorkflowDetail,
  WorkflowListItem,
  WorkflowStatusResponse
} from "./types";

type ActiveRun =
  | { kind: "message"; data: MessageSubmissionResponse }
  | { kind: "workflow"; data: WorkflowStatusResponse }
  | null;

function App() {
  const [runs, setRuns] = useState<WorkflowListItem[]>([]);
  const [activeRun, setActiveRun] = useState<ActiveRun>(null);
  const [message, setMessage] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [isLoadingRuns, setIsLoadingRuns] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void refreshRuns();
  }, []);

  const activeDetails = useMemo(() => readActiveRun(activeRun), [activeRun]);

  async function refreshRuns() {
    setIsLoadingRuns(true);
    try {
      const response = await listWorkflows();
      setRuns(response.workflows);
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setIsLoadingRuns(false);
    }
  }

  async function selectRun(workflowId: string) {
    setError(null);
    setSelectedWorkflowId(workflowId);
    try {
      setActiveRun({ kind: "workflow", data: await getWorkflow(workflowId) });
    } catch (caught) {
      setError(errorMessage(caught));
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!message.trim() || isSubmitting) {
      return;
    }

    setError(null);
    setIsSubmitting(true);
    setSelectedWorkflowId(null);
    try {
      const response = await submitMessage(message.trim(), files);
      setActiveRun({ kind: "message", data: response });
      setMessage("");
      await refreshRuns();
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="appShell">
      <aside className="sidebar" aria-label="Recent workflow runs">
        <div className="sidebarHeader">
          <h1>OpenAgentLab</h1>
          <p>Recent runs</p>
        </div>

        <button
          className="secondaryButton"
          type="button"
          onClick={() => {
            setActiveRun(null);
            setSelectedWorkflowId(null);
            setError(null);
          }}
        >
          Start run
        </button>

        <div className="runList" aria-live="polite">
          {isLoadingRuns ? <p className="muted">Loading runs...</p> : null}
          {!isLoadingRuns && runs.length === 0 ? (
            <p className="muted">No workflow runs yet.</p>
          ) : null}
          {runs.map((run) => (
            <button
              className={
                run.workflow_id === selectedWorkflowId
                  ? "runItem selected"
                  : "runItem"
              }
              key={run.workflow_id}
              type="button"
              onClick={() => void selectRun(run.workflow_id)}
            >
              <span>{run.display_label}</span>
              <small>
                {run.status} · {formatDate(run.created_at)}
              </small>
            </button>
          ))}
        </div>
      </aside>

      <section className="workspace" aria-label="Workflow run">
        <div className="runPanel">
          {error ? (
            <div className="errorBanner" role="alert">
              {error}
            </div>
          ) : null}
          {isSubmitting ? <StatusBlock status="pending" /> : null}
          {!isSubmitting && activeDetails ? (
            <RunDetails details={activeDetails} />
          ) : null}
          {!isSubmitting && !activeDetails ? <EmptyState /> : null}
        </div>

        <form className="composer" onSubmit={(event) => void handleSubmit(event)}>
          <label htmlFor="message">Question</label>
          <textarea
            id="message"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Ask a question for a new workflow run..."
            rows={3}
          />
          <div className="composerFooter">
            <label className="fileButton">
              Attach files
              <input
                multiple
                type="file"
                onChange={(event) =>
                  setFiles(Array.from(event.target.files ?? []))
                }
              />
            </label>
            <div className="pendingFiles" aria-live="polite">
              {files.map((file) => (
                <span key={`${file.name}-${file.size}`}>
                  {file.name} ({formatBytes(file.size)})
                </span>
              ))}
            </div>
            <button
              className="primaryButton"
              disabled={!message.trim() || isSubmitting}
              type="submit"
            >
              {isSubmitting ? "Running..." : "Send"}
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}

interface RunDetailsView {
  workflowId: string | null;
  sessionId: string | null;
  status: string;
  answer: string | null;
  error: string | null;
  attachments: AttachmentMetadata[];
  sources: Record<string, unknown>[];
  artifacts: Record<string, unknown>[];
  workflowDetails: WorkflowDetail[];
}

function RunDetails({ details }: { details: RunDetailsView }) {
  return (
    <article className="runDetails">
      <header>
        <StatusBlock status={details.status} />
        {details.workflowId ? (
          <p className="identifier">Run {details.workflowId}</p>
        ) : null}
      </header>

      {details.error ? (
        <div className="errorBanner" role="alert">
          {details.error}
        </div>
      ) : null}

      <section>
        <h2>Final answer</h2>
        <p className="answerText">
          {details.answer || "No final answer returned yet."}
        </p>
      </section>

      <AttachmentList attachments={details.attachments} />
      <ArtifactList artifacts={details.artifacts} />

      {details.workflowDetails.length ? (
        <details className="workflowDetails">
          <summary>Workflow details</summary>
          <ol>
            {details.workflowDetails.map((step, index) => (
              <li key={`${step.label}-${index}`}>
                <strong>{step.label}</strong>
                <span>{step.status}</span>
                {step.summary ? <p>{step.summary}</p> : null}
              </li>
            ))}
          </ol>
        </details>
      ) : null}
    </article>
  );
}

function StatusBlock({ status }: { status: string }) {
  return <div className={`status status-${status}`}>{status}</div>;
}

function AttachmentList({
  attachments
}: {
  attachments: AttachmentMetadata[];
}) {
  if (!attachments.length) {
    return null;
  }

  return (
    <section>
      <h2>Attached files</h2>
      <ul className="attachmentList">
        {attachments.map((attachment) => (
          <li key={attachment.document_id}>
            <span>{attachment.filename}</span>
            <small>
              {attachment.content_type || "unknown type"} ·{" "}
              {formatBytes(attachment.size_bytes)} · {attachment.status}
            </small>
          </li>
        ))}
      </ul>
      <p className="limitation">
        Files are stored for this run and readable uploaded contents are used as
        direct answer context.
      </p>
    </section>
  );
}

function ArtifactList({ artifacts }: { artifacts: Record<string, unknown>[] }) {
  return (
    <section>
      <h2>Artifacts</h2>
      {artifacts.length ? (
        <ul className="artifactList">
          {artifacts.map((artifact, index) => (
            <li key={index}>{artifactLabel(artifact)}</li>
          ))}
        </ul>
      ) : (
        <p className="muted">No artifacts returned.</p>
      )}
    </section>
  );
}

function EmptyState() {
  return (
    <div className="emptyState">
      <h2>Start a workflow run</h2>
      <p>
        Submit a question to execute the configured OpenAgentLab
        question-answering workflow.
      </p>
    </div>
  );
}

function readActiveRun(activeRun: ActiveRun): RunDetailsView | null {
  if (!activeRun) {
    return null;
  }

  if (activeRun.kind === "message") {
    return {
      workflowId: activeRun.data.workflow_id,
      sessionId: activeRun.data.session_id,
      status: activeRun.data.status,
      answer: activeRun.data.final_answer,
      error: null,
      attachments: activeRun.data.attachments,
      sources: activeRun.data.sources,
      artifacts: activeRun.data.artifacts,
      workflowDetails: activeRun.data.workflow_details
    };
  }

  const result = activeRun.data.result;
  return {
    workflowId: activeRun.data.workflow_id,
    sessionId: activeRun.data.session_id,
    status: activeRun.data.status,
    answer: result?.final_answer ?? result?.answer ?? null,
    error: activeRun.data.error,
    attachments: result?.attachments ?? [],
    sources: result?.sources ?? [],
    artifacts: result?.artifacts ?? [],
    workflowDetails: result?.workflow_details ?? []
  };
}

function artifactLabel(artifact: Record<string, unknown>): string {
  const filename = artifact.filename ?? artifact.name ?? artifact.title;
  return typeof filename === "string" ? filename : JSON.stringify(artifact);
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

function formatBytes(value: number): string {
  if (value < 1024) {
    return `${value} B`;
  }
  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`;
  }
  return `${(value / 1024 / 1024).toFixed(1)} MB`;
}

function errorMessage(caught: unknown): string {
  return caught instanceof Error ? caught.message : "Unexpected request failure.";
}

export default App;
