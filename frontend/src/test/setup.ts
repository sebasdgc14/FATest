import "@testing-library/jest-dom";

// Basic fetch mock utility; individual tests can override.
if (typeof globalThis.fetch === "undefined") {
  const placeholder = async (): Promise<Response> => {
    throw new Error("fetch not mocked in test");
  };
  globalThis.fetch = placeholder as unknown as typeof fetch;
}
