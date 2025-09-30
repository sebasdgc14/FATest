import { useEffect, useState, useMemo } from "react";
import { API_BASE } from "../config";

interface ComplianceDefinition {
  id: string;
  title: string;
  link?: string | null;
}

interface ComplianceLang {
  summary?: string | null;
}

interface ComplianceItem {
  id: string;
  title: string;
  en?: ComplianceLang;
  es?: ComplianceLang;
  definitions?: ComplianceDefinition[];
  metadata?: Record<string, unknown>;
  last_update_time?: string;
}

function getInitialLang(): "en" | "es" | "both" {
  const p = new URLSearchParams(window.location.search);
  const l = p.get("lang");
  return l === "en" || l === "es" || l === "both" ? l : "both";
}

async function fetchCompliance(lang: "en" | "es" | "both"): Promise<ComplianceItem[]> {
  const base = `${API_BASE}/api/compliance`;
  const url = lang === "both" ? base : `${base}?lang=${lang}`;
  const res = await fetch(url);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to load compliance: ${res.status} ${text}`);
  }
  return res.json();
}

export default function CompliancePage() {
  const [lang, setLang] = useState<"en" | "es" | "both">(getInitialLang);
  const [data, setData] = useState<ComplianceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchCompliance(lang)
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

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (lang === "both") params.delete("lang");
    else params.set("lang", lang);
    const qs = params.toString();
    const newUrl = `${window.location.pathname}${qs ? "?" + qs : ""}`;
    window.history.replaceState(null, "", newUrl);
  }, [lang]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return data;
    return data.filter(
      (item) =>
        (item.id && item.id.toLowerCase().includes(q)) ||
        (item.title && item.title.toLowerCase().includes(q))
    );
  }, [data, search]);

  return (
    <div style={{ textAlign: "left" }}>
      <h1>Compliance</h1>
      <div
        style={{
          display: "flex",
          gap: "1rem",
          flexWrap: "wrap",
          marginBottom: "1rem",
          alignItems: "center",
        }}
      >
        <label style={{ fontSize: ".85rem" }}>
          Language:&nbsp;
          <select value={lang} onChange={(e) => setLang(e.target.value as "en" | "es" | "both")}>
            <option value="both">Both</option>
            <option value="en">English</option>
            <option value="es">Spanish</option>
          </select>
        </label>
        <label style={{ fontSize: ".85rem" }}>
          Search:&nbsp;
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search id / title"
          />
        </label>
        {search && <button onClick={() => setSearch("")}>Clear</button>}
        <span style={{ fontSize: ".7rem", opacity: 0.65 }}>
          Showing {filtered.length} of {data.length}
        </span>
      </div>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "salmon" }}>{error}</p>}
      <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: "1rem" }}>
        {filtered.map((item) => {
          const subtitleParts: string[] = [];
          if (item.last_update_time) {
            let d: string;
            try {
              d = new Date(item.last_update_time).toLocaleDateString();
            } catch {
              d = item.last_update_time;
            }
            subtitleParts.push(`Updated: ${d}`);
          }
          return (
            <li
              key={item.id}
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
                <h2 style={{ margin: 0 }}>{item.title}</h2>
                <code style={{ fontSize: ".7rem", opacity: 0.75 }}>{item.id}</code>
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
              <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginTop: ".5rem" }}>
                {item.en && (
                  <div style={{ flex: 1, minWidth: 260 }}>
                    <h3 style={{ margin: ".25rem 0 .25rem" }}>EN</h3>
                    <p
                      style={{
                        whiteSpace: "pre-wrap",
                        margin: 0,
                        fontSize: ".85rem",
                        lineHeight: "1.35",
                      }}
                    >
                      {item.en.summary || "—"}
                    </p>
                  </div>
                )}
                {item.es && (
                  <div style={{ flex: 1, minWidth: 260 }}>
                    <h3 style={{ margin: ".25rem 0 .25rem" }}>ES</h3>
                    <p
                      style={{
                        whiteSpace: "pre-wrap",
                        margin: 0,
                        fontSize: ".85rem",
                        lineHeight: "1.35",
                      }}
                    >
                      {item.es.summary || "—"}
                    </p>
                  </div>
                )}
              </div>
              {item.definitions?.length ? (
                <details style={{ marginTop: ".6rem" }}>
                  <summary style={{ cursor: "pointer", fontSize: ".75rem", fontWeight: 600 }}>
                    Definitions ({item.definitions.length})
                  </summary>
                  <div
                    style={{ marginTop: ".5rem", display: "flex", flexWrap: "wrap", gap: ".4rem" }}
                  >
                    {item.definitions.map((def) => {
                      const clickable = !!def.link;
                      return (
                        <button
                          key={def.id}
                          onClick={() => clickable && window.open(def.link!, "_blank", "noopener")}
                          title={`${def.id}: ${def.title}${clickable ? " (open link)" : ""}`}
                          disabled={!clickable}
                          style={{
                            background: clickable ? "#3a3a3a" : "#2d2d2d",
                            border: "1px solid #555",
                            borderRadius: "4px",
                            padding: ".25rem .5rem",
                            fontSize: ".6rem",
                            cursor: clickable ? "pointer" : "default",
                            opacity: clickable ? 1 : 0.55,
                            maxWidth: "140px",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                            overflow: "hidden",
                          }}
                        >
                          {def.id}
                        </button>
                      );
                    })}
                  </div>
                </details>
              ) : null}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
