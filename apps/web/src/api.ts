import type {
  MessageSubmissionResponse,
  WorkflowListResponse,
  WorkflowStatusResponse
} from "./types";

interface ApiErrorPayload {
  error?: {
    code?: string;
    message?: string;
  };
}

export async function listWorkflows(): Promise<WorkflowListResponse> {
  return requestJson<WorkflowListResponse>("/api/v1/workflows");
}

export async function getWorkflow(
  workflowId: string
): Promise<WorkflowStatusResponse> {
  return requestJson<WorkflowStatusResponse>(`/api/v1/workflows/${workflowId}`);
}

export async function submitMessage(
  message: string,
  files: File[]
): Promise<MessageSubmissionResponse> {
  const formData = new FormData();
  formData.append("message", message);
  for (const file of files) {
    formData.append("files", file);
  }

  return requestJson<MessageSubmissionResponse>("/api/v1/messages", {
    method: "POST",
    body: formData
  });
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) {
    let message = `Request failed with status ${response.status}.`;
    try {
      const payload = (await response.json()) as ApiErrorPayload;
      if (payload.error?.message) {
        message = payload.error.message;
      }
    } catch {
      // Keep the status-based fallback.
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}
