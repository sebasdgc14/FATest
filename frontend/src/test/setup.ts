import "@testing-library/jest-dom";

// Basic fetch mock utility; individual tests can override
if (!(globalThis as any).fetch) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (globalThis as any).fetch = (async () => {
    throw new Error("fetch not mocked in test");
  }) as any;
}
