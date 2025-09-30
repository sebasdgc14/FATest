import { render, screen, fireEvent } from "@testing-library/react";
import { vi } from "vitest";
import SolutionsPage from "../SolutionsPage";
import { beforeEach } from "vitest";
import { afterEach } from "vitest";
import { test } from "vitest";
import { expect } from "vitest";

beforeEach(() => {
  // First call: index; second call: dataset
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ datasets: [{ name: "python", count: 1 }] }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [
          {
            vulnerability_id: "VULN-1",
            title: "Python Issue",
            context: ["context line"],
            need: "Fix something",
            solution: {
              language: "python",
              steps: ["one", "two"],
              insecure_code_example: { text: "bad()" },
              secure_code_example: { text: "good()" },
            },
            last_update_time: null,
          },
        ],
      })
  );
});

afterEach(() => {
  vi.restoreAllMocks();
});

test("loads index then dataset and filters by search", async () => {
  render(<SolutionsPage />);
  // Wait for the option inside the select (role=option)
  const option = await screen.findByRole("option", { name: /python/i });
  expect(option).toBeInTheDocument();
  const select = screen.getByLabelText(/dataset:/i);
  fireEvent.change(select, { target: { value: "python" } });
  // Now the dataset entry should appear
  expect(await screen.findByText(/Python Issue/)).toBeInTheDocument();
  const searchInput = screen.getByPlaceholderText(/search title/i);
  fireEvent.change(searchInput, { target: { value: "nomatch" } });
  expect(screen.queryByText(/Python Issue/)).not.toBeInTheDocument();
});
