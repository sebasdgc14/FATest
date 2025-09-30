import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import VulnerabilitiesPage from "../VulnerabilitiesPage";
import { beforeEach } from "vitest";
import { afterEach } from "vitest";
import { test } from "vitest";
import { expect } from "vitest";

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [
        {
          id: "VULN-1",
          category: "auth",
          en: {
            title: "Auth Issue",
            description: "D",
            impact: "I",
            recommendation: "R",
            threat: "T",
          },
          es: null,
          requirements: ["REQ-1"],
          metadata: {},
          last_update_time: null,
        },
      ],
    })
  );
});

afterEach(() => {
  vi.restoreAllMocks();
});

test("renders vulnerabilities heading and vulnerability id", async () => {
  render(<VulnerabilitiesPage />);
  expect(screen.getByRole("heading", { name: /vulnerabilities/i })).toBeInTheDocument();
  expect(await screen.findByText("VULN-1")).toBeInTheDocument();
});
