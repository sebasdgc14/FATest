import { useEffect, useState, useMemo } from "react";
import { API_BASE } from "../config";

interface SolutionsIndexItem {
  name: string;
  count?: number;
  error?: string;
}

interface SolutionCodeExample {
  description?: string;
  text?: string;
}

interface SolutionDetails {
  language?: string;
  insecure_code_example?: SolutionCodeExample;
  secure_code_example?: SolutionCodeExample;
  steps?: string[];
}

interface SolutionEntry {
  vulnerability_id?: string;
  title: string;
  context?: string[];
  need?: string;
  solution?: SolutionDetails;
  last_update_time?: string;
}

interface SolutionsIndexResponse {
  datasets: SolutionsIndexItem[];
}

async function fetchSolutionsIndex(): Promise<SolutionsIndexResponse> {
  const res = await fetch(`${API_BASE}/api/solutions/index`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to load solutions index: ${res.status} ${text}`);
  }
  return res.json();
}

async function fetchSolutionsDataset(name: string): Promise<SolutionEntry[]> {
  const url = `${API_BASE}/api/solutions?name=${encodeURIComponent(name)}`;
  const res = await fetch(url);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to load solutions dataset '${name}': ${res.status} ${text}`);
  }
  return res.json();
}

function getInitialDataset(): string {
  const p = new URLSearchParams(window.location.search);
  return p.get("solutions") || "";
}

function getInitialQuery(): string {
  const p = new URLSearchParams(window.location.search);
  return p.get("q") || "";
}

export default function SolutionsPage() {
  const [indexData, setIndexData] = useState<SolutionsIndexItem[]>([]);
  const [dataset, setDataset] = useState<string>(getInitialDataset);
  const [entries, setEntries] = useState<SolutionEntry[]>([]);
  const [loadingIndex, setLoadingIndex] = useState(false);
  const [loadingDataset, setLoadingDataset] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState<string>(getInitialQuery);

  useEffect(() => {
    let cancelled = false;
    setLoadingIndex(true);
    fetchSolutionsIndex()
      .then((json) => {
        if (!cancelled) setIndexData(json.datasets || []);
      })
      .catch((e) => {
        if (!cancelled) setError(e.message);
      })
      .finally(() => {
        if (!cancelled) setLoadingIndex(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!dataset) {
      setEntries([]);
      return;
    }
    let cancelled = false;
    setLoadingDataset(true);
    setError(null);
    fetchSolutionsDataset(dataset)
      .then((json) => {
        if (!cancelled) setEntries(json);
      })
      .catch((e) => {
        if (!cancelled) setError(e.message);
      })
      .finally(() => {
        if (!cancelled) setLoadingDataset(false);
      });
    return () => {
      cancelled = true;
    };
  }, [dataset]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (dataset) params.set("solutions", dataset);
    else params.delete("solutions");
    if (query) params.set("q", query);
    else params.delete("q");
    const qs = params.toString();
    const newUrl = `${window.location.pathname}${qs ? "?" + qs : ""}`;
    window.history.replaceState(null, "", newUrl);
  }, [dataset, query]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return entries;
    return entries.filter(
      (e) =>
        (e.title && e.title.toLowerCase().includes(q)) ||
        (e.vulnerability_id && e.vulnerability_id.toLowerCase().includes(q)) ||
        (Array.isArray(e.context) && e.context.some((c) => (c || "").toLowerCase().includes(q))) ||
        (e.need && e.need.toLowerCase().includes(q))
    );
  }, [entries, query]);

  return (
    <div style={{ textAlign: "left" }}>
      <h1>Solutions</h1>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "1rem",
          alignItems: "center",
          marginBottom: "1rem",
        }}
      >
        <label style={{ fontSize: ".85rem" }}>
          Dataset:&nbsp;
          <select value={dataset} onChange={(e) => setDataset(e.target.value)}>
            <option value="">-- choose --</option>
            {indexData.map((d) => (
              <option key={d.name} value={d.name}>
                {d.name}
                {typeof d.count === "number" ? ` (${d.count})` : ""}
              </option>
            ))}
          </select>
        </label>
        {dataset && (
          <label style={{ fontSize: ".85rem" }}>
            Search:&nbsp;
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search title / id / context / need"
            />
          </label>
        )}
        {query && <button onClick={() => setQuery("")}>Clear</button>}
        {dataset && <button onClick={() => setDataset("")}>Close dataset</button>}
        {dataset && (
          <span style={{ fontSize: ".7rem", opacity: 0.65 }}>
            Showing {filtered.length} of {entries.length}
          </span>
        )}
      </div>
      {loadingIndex && <p>Loading index...</p>}
      {loadingDataset && <p>Loading dataset...</p>}
      {error && <p style={{ color: "salmon" }}>{error}</p>}
      {!dataset && !loadingIndex && indexData.length === 0 && (
        <p style={{ fontSize: ".8rem", opacity: 0.7 }}>No solution datasets available.</p>
      )}
      {!dataset && indexData.length > 0 && (
        <ul
          style={{
            listStyle: "none",
            padding: 0,
            display: "flex",
            flexWrap: "wrap",
            gap: ".75rem",
          }}
        >
          {indexData.map((d) => (
            <li key={d.name}>
              <button
                onClick={() => setDataset(d.name)}
                style={{
                  background: "#2d2d2d",
                  border: "1px solid #444",
                  padding: ".6rem .9rem",
                  borderRadius: 8,
                  cursor: "pointer",
                  fontSize: ".75rem",
                }}
                title={d.error ? d.error : `${d.count ?? "?"} entries`}
                disabled={!!d.error}
              >
                <strong style={{ fontWeight: 600 }}>{d.name}</strong>
                {typeof d.count === "number" && (
                  <span style={{ opacity: 0.6 }}> &ndash; {d.count}</span>
                )}
                {d.error && (
                  <span style={{ color: "salmon", marginLeft: ".4rem" }}>({d.error})</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
      {dataset && (
        <ul
          style={{
            listStyle: "none",
            padding: 0,
            display: "grid",
            gap: "1rem",
            marginTop: ".5rem",
          }}
        >
          {filtered.map((sol) => {
            const insecure = sol.solution?.insecure_code_example;
            const secure = sol.solution?.secure_code_example;
            const steps = sol.solution?.steps || [];
            const subtitleParts: string[] = [];
            if (sol.last_update_time) {
              let d: string;
              try {
                d = new Date(sol.last_update_time).toLocaleDateString();
              } catch {
                d = sol.last_update_time;
              }
              subtitleParts.push(`Updated: ${d}`);
            }
            return (
              <li
                key={(sol.vulnerability_id || "") + sol.title}
                style={{
                  border: "1px solid #444",
                  borderRadius: 8,
                  padding: "1rem",
                  background: "#2d2d2d",
                }}
              >
                <header
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "baseline",
                    gap: "1rem",
                  }}
                >
                  <h2 style={{ margin: 0 }}>{sol.title}</h2>
                  {sol.vulnerability_id && (
                    <code style={{ fontSize: ".65rem", opacity: 0.75 }}>
                      {sol.vulnerability_id}
                    </code>
                  )}
                </header>
                {subtitleParts.length > 0 && (
                  <div
                    style={{
                      fontSize: ".6rem",
                      opacity: 0.7,
                      marginTop: ".25rem",
                      display: "flex",
                      flexWrap: "wrap",
                      gap: ".4rem",
                    }}
                  >
                    {subtitleParts.map((part) => (
                      <span
                        key={part}
                        style={{ background: "#3a3a3a", padding: ".15rem .45rem", borderRadius: 4 }}
                      >
                        {part}
                      </span>
                    ))}
                  </div>
                )}
                {sol.context?.length ? (
                  <div style={{ marginTop: ".6rem" }}>
                    <div
                      style={{
                        fontSize: ".6rem",
                        fontWeight: 600,
                        opacity: 0.75,
                        textTransform: "uppercase",
                        letterSpacing: ".5px",
                      }}
                    >
                      Context
                    </div>
                    <div
                      style={{
                        marginTop: ".35rem",
                        fontSize: ".6rem",
                        lineHeight: 1.4,
                        whiteSpace: "pre-wrap",
                      }}
                    >
                      {sol.context.join("\n")}
                    </div>
                  </div>
                ) : null}
                {sol.need && (
                  <p style={{ margin: ".7rem 0 .4rem", fontSize: ".7rem", lineHeight: 1.4 }}>
                    <span style={{ fontWeight: 600 }}>need:</span> {sol.need}
                  </p>
                )}
                <details style={{ marginTop: ".4rem" }}>
                  <summary style={{ cursor: "pointer", fontSize: ".65rem", fontWeight: 700 }}>
                    code examples
                  </summary>
                  <div
                    style={{ display: "flex", flexWrap: "wrap", gap: "1rem", marginTop: ".6rem" }}
                  >
                    {insecure?.text && (
                      <div style={{ flex: 1, minWidth: 280 }}>
                        <div
                          style={{
                            fontSize: ".6rem",
                            fontWeight: 600,
                            opacity: 0.8,
                            marginBottom: ".3rem",
                          }}
                        >
                          Insecure
                        </div>
                        {insecure.description && (
                          <pre
                            style={{
                              background: "#1e1e1e",
                              padding: ".4rem",
                              borderRadius: 6,
                              fontSize: ".55rem",
                              whiteSpace: "pre-wrap",
                              marginBottom: ".35rem",
                            }}
                          >
                            {insecure.description}
                          </pre>
                        )}
                        <pre
                          style={{
                            background: "#1e1e1e",
                            padding: ".5rem",
                            borderRadius: 6,
                            fontSize: ".55rem",
                            overflowX: "auto",
                          }}
                        >
                          <code>{insecure.text}</code>
                        </pre>
                      </div>
                    )}
                    {secure?.text && (
                      <div style={{ flex: 1, minWidth: 280 }}>
                        <div
                          style={{
                            fontSize: ".6rem",
                            fontWeight: 600,
                            opacity: 0.8,
                            marginBottom: ".3rem",
                          }}
                        >
                          Secure
                        </div>
                        {secure.description && (
                          <pre
                            style={{
                              background: "#1e1e1e",
                              padding: ".4rem",
                              borderRadius: 6,
                              fontSize: ".55rem",
                              whiteSpace: "pre-wrap",
                              marginBottom: ".35rem",
                            }}
                          >
                            {secure.description}
                          </pre>
                        )}
                        <pre
                          style={{
                            background: "#1e1e1e",
                            padding: ".5rem",
                            borderRadius: 6,
                            fontSize: ".55rem",
                            overflowX: "auto",
                          }}
                        >
                          <code>{secure.text}</code>
                        </pre>
                      </div>
                    )}
                  </div>
                </details>
                {steps.length > 0 && (
                  <details style={{ marginTop: ".7rem" }}>
                    <summary style={{ cursor: "pointer", fontSize: ".65rem", fontWeight: 700 }}>
                      steps ({steps.length})
                    </summary>
                    <ol
                      style={{
                        marginTop: ".5rem",
                        paddingLeft: "1.2rem",
                        fontSize: ".6rem",
                        lineHeight: 1.4,
                      }}
                    >
                      {steps.map((s, i) => (
                        <li key={i} style={{ marginBottom: ".35rem" }}>
                          {s}
                        </li>
                      ))}
                    </ol>
                  </details>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
