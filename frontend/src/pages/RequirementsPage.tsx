import { useEffect, useState, useMemo } from "react";
import { API_BASE } from "../config";

interface RequirementLang {
  title: string;
  summary: string;
  description: string;
}

interface RequirementItem {
  id: string;
  category?: string | null;
  en?: RequirementLang;
  es?: RequirementLang;
  supported_in?: Record<string, boolean | null | undefined> | null;
  references?: string[];
  metadata?: Record<string, unknown>;
  last_update_time?: string;
}

function getInitialLang(): "en" | "es" | "both" {
  const p = new URLSearchParams(window.location.search);
  const l = p.get("lang");
  if (l === "en" || l === "es" || l === "both") return l;
  return "both";
}

async function fetchRequirements(lang: "en" | "es" | "both"): Promise<RequirementItem[]> {
  const base = `${API_BASE}/api/requirements`;
  const url = lang === "both" ? base : `${base}?lang=${lang}`;
  const res = await fetch(url);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to load requirements: ${res.status} ${text}`);
  }
  return res.json();
}

export default function RequirementsPage() {
  const [lang, setLang] = useState<"en" | "es" | "both">(getInitialLang);
  const [data, setData] = useState<RequirementItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refFilter, setRefFilter] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchRequirements(lang)
      .then((json) => {
        if (!cancelled) setData(json);
      })
      .catch((e) => {
        if (!cancelled) setError(e.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [lang]);

  // Sync lang to URL (replaceState avoids history spam)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (lang === "both") params.delete("lang");
    else params.set("lang", lang);
    const qs = params.toString();
    const newUrl = `${window.location.pathname}${qs ? "?" + qs : ""}`;
    window.history.replaceState(null, "", newUrl);
  }, [lang]);

  const filtered = useMemo(() => {
    const q = refFilter.trim().toLowerCase();
    if (!q) return data;
    return data.filter(
      (r) =>
        Array.isArray(r.references) &&
        r.references.some((ref) => (ref || "").toLowerCase().includes(q))
    );
  }, [data, refFilter]);

  return (
    <div style={{ textAlign: "left" }}>
      <h1>Requirements</h1>
      <div style={{ marginBottom: "1rem" }}>
        <label style={{ fontSize: ".85rem" }}>
          Language:&nbsp;
          <select value={lang} onChange={(e) => setLang(e.target.value as "en" | "es" | "both")}>
            <option value="both">Both</option>
            <option value="en">English</option>
            <option value="es">Spanish</option>
          </select>
        </label>
        <label style={{ fontSize: ".85rem", marginLeft: "1rem" }}>
          Reference filter:&nbsp;
          <input
            value={refFilter}
            onChange={(e) => setRefFilter(e.target.value)}
            placeholder="Input reference to filter available data."
            style={{ width: "220px" }}
          />
        </label>
        {refFilter && (
          <button style={{ marginLeft: ".5rem" }} onClick={() => setRefFilter("")}>
            Clear
          </button>
        )}
      </div>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "salmon" }}>{error}</p>}
      <p style={{ fontSize: ".75rem", opacity: 0.7, marginTop: "-.5rem" }}>
        Showing {filtered.length} of {data.length} requirements{refFilter && " (filtered)"}
      </p>
      <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: "1rem" }}>
        {filtered.map((r) => {
          const subtitleParts: string[] = [];
          if (r.category) subtitleParts.push(`Category: ${r.category}`);
          if (r.last_update_time) {
            let d: string;
            try {
              d = new Date(r.last_update_time).toLocaleDateString();
            } catch {
              d = r.last_update_time;
            }
            subtitleParts.push(`Updated: ${d}`);
          }
          return (
            <li
              key={r.id}
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
                <h2 style={{ margin: 0 }}>{r.en?.title || r.es?.title || r.id}</h2>
                <code style={{ fontSize: ".75rem", opacity: 0.8 }}>{r.id}</code>
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
              <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
                {r.en && (
                  <div style={{ flex: 1, minWidth: 260 }}>
                    <h3 style={{ margin: ".5rem 0 .25rem" }}>EN</h3>
                    <p style={{ margin: ".25rem 0", fontWeight: 500 }}>{r.en.summary}</p>
                    <p
                      style={{
                        whiteSpace: "pre-wrap",
                        margin: ".25rem 0",
                        fontSize: ".85rem",
                        lineHeight: "1.35",
                      }}
                    >
                      {r.en.description}
                    </p>
                  </div>
                )}
                {r.es && (
                  <div style={{ flex: 1, minWidth: 260 }}>
                    <h3 style={{ margin: ".5rem 0 .25rem" }}>ES</h3>
                    <p style={{ margin: ".25rem 0", fontWeight: 500 }}>{r.es.summary}</p>
                    <p
                      style={{
                        whiteSpace: "pre-wrap",
                        margin: ".25rem 0",
                        fontSize: ".85rem",
                        lineHeight: "1.35",
                      }}
                    >
                      {r.es.description}
                    </p>
                  </div>
                )}
              </div>
              {r.references?.length ? (
                <div
                  style={{
                    marginTop: ".5rem",
                    display: "flex",
                    flexWrap: "wrap",
                    gap: ".4rem",
                    alignItems: "center",
                  }}
                >
                  <strong style={{ marginRight: ".25rem" }}>References:</strong>
                  {r.references.map((ref) => (
                    <span
                      key={ref}
                      style={{
                        background: "#3a3a3a",
                        padding: ".15rem .4rem",
                        borderRadius: "4px",
                        fontSize: ".65rem",
                        maxWidth: "320px",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                      title={ref}
                    >
                      {/https?:/i.test(ref) ? (
                        <a
                          href={ref}
                          target="_blank"
                          rel="noreferrer"
                          style={{ color: "inherit", textDecoration: "none" }}
                        >
                          {ref}
                        </a>
                      ) : (
                        ref
                      )}
                    </span>
                  ))}
                </div>
              ) : null}
              {r.supported_in && (
                <div style={{ marginTop: ".5rem", fontSize: ".7rem", opacity: 0.8 }}>
                  <strong>Supported In:</strong>{" "}
                  {Object.entries(r.supported_in).map(([k, v]) => (
                    <span key={k} style={{ marginRight: ".5rem" }}>
                      {k}:{v === true ? "yes" : v === false ? "no" : "n/a"}
                    </span>
                  ))}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
