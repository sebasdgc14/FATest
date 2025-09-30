import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import CompliancePage from "../CompliancePage";
import { beforeEach } from "vitest";
import { afterEach } from "vitest";
import { it } from "vitest";
import { expect } from "vitest";

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [
        {
          id: "C-1",
          title: "Control 1",
          en: { summary: "English summary" },
          es: null,
          definitions: [],
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

it("renders compliance heading and item", async () => {
  render(<CompliancePage />);
  expect(screen.getByRole("heading", { name: /compliance/i })).toBeInTheDocument();
  expect(await screen.findByText("Control 1")).toBeInTheDocument();
});
