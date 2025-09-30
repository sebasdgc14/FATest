import { render, screen } from "@testing-library/react";
import RequirementsPage from "../RequirementsPage";
import { vi } from "vitest";
import { beforeEach } from "vitest";
import { afterEach } from "vitest";
import { expect } from "vitest";
import { test } from "vitest";

// Minimal mock fetch returning one requirement
beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [
        {
          id: "REQ-1",
          category: "general",
          en: { title: "Title EN", summary: "S", description: "D" },
          es: null,
          references: ["RFC-1"],
          supported_in: { python: true },
          metadata: { level: "base" },
          last_update_time: null,
        },
      ],
    })
  );
});

afterEach(() => {
  vi.restoreAllMocks();
});

test("renders heading and requirement id after fetch", async () => {
  render(<RequirementsPage />);
  expect(screen.getByRole("heading", { name: /requirements/i })).toBeInTheDocument();
  expect(await screen.findByText("REQ-1")).toBeInTheDocument();
});
