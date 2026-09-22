import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const workflowList = {
  workflows: [
    {
      workflow_id: "11111111-1111-4111-8111-111111111111",
      session_id: "22222222-2222-4222-8222-222222222222",
      status: "completed",
      display_label: "What changed?",
      created_at: "2026-08-11T12:00:00Z",
      updated_at: "2026-08-11T12:00:00Z",
      started_at: "2026-08-11T12:00:00Z",
      finished_at: "2026-08-11T12:00:00Z"
    }
  ]
};

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const path = String(input);
        if (path === "/api/v1/workflows") {
          return jsonResponse(workflowList);
        }
        if (path === "/api/v1/messages") {
          return jsonResponse({
            workflow_id: "33333333-3333-4333-8333-333333333333",
            session_id: "44444444-4444-4444-8444-444444444444",
            status: "completed",
            final_answer: "The indexed evidence points to growth.",
            attachments: [
              {
                document_id: "55555555-5555-4555-8555-555555555555",
                filename: "report.txt",
                content_type: "text/plain",
                size_bytes: 5,
                status: "stored"
              }
            ],
            sources: [],
            artifacts: [],
            workflow_details: [
              {
                label: "Store attachments",
                status: "completed",
                summary:
                  "1 file(s) stored. 1 uploaded file(s) used as direct answer context."
              }
            ]
          });
        }
        return jsonResponse({}, 404);
      })
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("submits a run and shows truthful attachment metadata", async () => {
    render(<App />);

    expect(await screen.findByText("Recent runs")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Question"), {
      target: { value: "What changed?" }
    });
    fireEvent.change(screen.getByLabelText("Attach files"), {
      target: {
        files: [new File(["hello"], "report.txt", { type: "text/plain" })]
      }
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await screen.findByText("The indexed evidence points to growth.");
    expect(screen.getAllByText("completed").length).toBeGreaterThan(0);
    expect(
      screen.getByText("The indexed evidence points to growth.")
    ).toBeInTheDocument();
    expect(screen.getByText("report.txt")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Files are stored for this run and readable uploaded contents are used as direct answer context."
      )
    ).toBeInTheDocument();

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith("/api/v1/messages", expect.any(Object));
    });
  });

  it("shows a recoverable message when question answering is unavailable", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const path = String(input);
      if (path === "/api/v1/workflows") {
        return jsonResponse(workflowList);
      }
      if (path === "/api/v1/messages") {
        return jsonResponse(
          {
            error: {
              code: "QUESTION_ANSWERING_UNAVAILABLE",
              message:
                "Question-answering service is unavailable because Qdrant is not configured. Set QDRANT_URL before retrying.",
              details: null
            }
          },
          503
        );
      }
      return jsonResponse({}, 404);
    });

    render(<App />);

    expect(await screen.findByText("Recent runs")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Question"), {
      target: { value: "What changed?" }
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Question-answering service is unavailable because Qdrant is not configured. Set QDRANT_URL before retrying."
    );
    expect(screen.getByLabelText("Question")).toHaveValue("What changed?");
    expect(screen.getByRole("button", { name: "Send" })).toBeEnabled();
  });
});

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" }
  });
}
