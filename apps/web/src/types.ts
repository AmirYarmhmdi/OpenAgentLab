export type WorkflowStatus = "pending" | "running" | "completed" | "failed" | string;

export interface WorkflowListItem {
  workflow_id: string;
  session_id: string;
  status: WorkflowStatus;
  display_label: string;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export interface WorkflowListResponse {
  workflows: WorkflowListItem[];
}

export interface AttachmentMetadata {
  document_id: string;
  filename: string;
  content_type: string | null;
  size_bytes: number;
  status: string;
}

export interface WorkflowDetail {
  label: string;
  status: string;
  summary: string | null;
}

export interface MessageSubmissionResponse {
  workflow_id: string | null;
  session_id: string | null;
  status: WorkflowStatus;
  final_answer: string;
  attachments: AttachmentMetadata[];
  sources: Record<string, unknown>[];
  artifacts: Record<string, unknown>[];
  workflow_details: WorkflowDetail[];
}

export interface WorkflowStatusResponse {
  workflow_id: string;
  session_id: string;
  status: WorkflowStatus;
  result: {
    answer?: string;
    final_answer?: string;
    attachments?: AttachmentMetadata[];
    sources?: Record<string, unknown>[];
    artifacts?: Record<string, unknown>[];
    workflow_details?: WorkflowDetail[];
  } | null;
  error: string | null;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  finished_at: string | null;
}
