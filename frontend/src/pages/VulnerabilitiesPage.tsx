import { useEffect, useState, useMemo } from "react";
import yaml from "js-yaml";
import { API_BASE } from "../config";

interface VulnerabilityLang {
  title: string;
  description: string;
  impact: string;
  recommendation: string;
  threat: string;
}

interface VulnerabilityExamples {
  non_compliant?: string;
  compliant?: string;
}

interface VulnerabilityScoreBase {
  attack_vector?: string;
  attack_complexity?: string;
  privileges_required?: string;
  user_interaction?: string;
  scope?: string;
  confidentiality?: string;
  integrity?: string;
  availability?: string;
}

interface VulnerabilityScoreTemporal {
  exploit_code_maturity?: string;
  remediation_level?: string;
  report_confidence?: string;
}

interface VulnerabilityScore {
  base?: VulnerabilityScoreBase;
  temporal?: VulnerabilityScoreTemporal;
}

interface VulnerabilityScoreV4Base {
  attack_vector?: string;
  attack_complexity?: string;
  attack_requirements?: string;
  privileges_required?: string;
  user_interaction?: string;
  confidentiality_vc?: string;
  integrity_vi?: string;
  availability_va?: string;
  confidentiality_sc?: string;
  integrity_si?: string;
  availability_sa?: string;
}

interface VulnerabilityScoreV4Threat {
  exploit_maturity?: string;
}

interface VulnerabilityScoreV4 {
  base?: VulnerabilityScoreV4Base;
  threat?: VulnerabilityScoreV4Threat;
}

interface VulnerabilityItem {
  id: string;
  category?: string;
  en?: VulnerabilityLang;
  es?: VulnerabilityLang;
  examples?: VulnerabilityExamples;
  remediation_time?: string;
  score?: VulnerabilityScore;
  score_v4?: VulnerabilityScoreV4;
  requirements?: string[];
  metadata?: Record<string, unknown>;
  last_update_time?: string;
}

type LangChoice = "en" | "es" | "both";

function getInitialLang(): LangChoice {
  const p = new URLSearchParams(window.location.search);
  const l = p.get("lang");
  return l === "en" || l === "es" || l === "both" ? l : "both";
}

async function fetchVulnerabilities(lang: LangChoice): Promise<VulnerabilityItem[]> {
  const base = `${API_BASE}/api/vulnerabilities`;
  const url = lang === "both" ? base : `${base}?lang=${lang}`;
  const res = await fetch(url);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to load vulnerabilities: ${res.status} ${text}`);
  }
  return res.json();
}

export default function VulnerabilitiesPage() {
  const [lang, setLang] = useState<LangChoice>(getInitialLang);
  const [data, setData] = useState<VulnerabilityItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [reqFilter, setReqFilter] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchVulnerabilities(lang)
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
    const catQ = search.trim().toLowerCase();
    const rq = reqFilter.trim().toLowerCase();
    return data.filter((v) => {
      let matchCategory = true;
      if (catQ) matchCategory = (v.category || "").toLowerCase().includes(catQ);
      let matchReq = true;
      if (rq)
        matchReq =
          Array.isArray(v.requirements) &&
          v.requirements.some((rid) => (rid || "").toLowerCase().includes(rq));
      return matchCategory && matchReq;
    });
  }, [data, search, reqFilter]);

  return (
    <div style={{ textAlign: "left" }}>
      <h1>Vulnerabilities</h1>
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
          <select value={lang} onChange={(e) => setLang(e.target.value as LangChoice)}>
            <option value="both">Both</option>
            <option value="en">English</option>
            <option value="es">Spanish</option>
          </select>
        </label>
        <label style={{ fontSize: ".85rem" }}>
          Category filter:&nbsp;
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter by category"
          />
        </label>
        {search && <button onClick={() => setSearch("")}>Clear</button>}
        <label style={{ fontSize: ".85rem" }}>
          Requirement filter:&nbsp;
          <input
            value={reqFilter}
            onChange={(e) => setReqFilter(e.target.value)}
            placeholder="Req id substring"
          />
        </label>
        {reqFilter && <button onClick={() => setReqFilter("")}>Clear Req</button>}
        <span style={{ fontSize: ".7rem", opacity: 0.65 }}>
          Showing {filtered.length} of {data.length}
        </span>
      </div>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "salmon" }}>{error}</p>}
      <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: "1rem" }}>
        {filtered.map((v) => {
          const scoreBase = v.score?.base || {};
          const scoreTemporal = v.score?.temporal || {};
          const scoreV4Base = v.score_v4?.base || {};
          const scoreV4Threat = v.score_v4?.threat || {};
          const metaEntries = Object.entries(v.metadata || {}).filter(
            ([, val]) => val !== null && val !== undefined
          );

          const subtitleParts: string[] = [];
          if (v.id) subtitleParts.push(`ID: ${v.id}`);
          if (v.category) subtitleParts.push(`Category: ${v.category}`);
          if (v.remediation_time) subtitleParts.push(`Remediation: ${v.remediation_time}`);
          if (v.last_update_time) {
            let d: string;
            try {
              d = new Date(v.last_update_time).toLocaleDateString();
            } catch {
              d = v.last_update_time;
            }
            subtitleParts.push(`Updated: ${d}`);
          }

          const renderKVGroup = (obj: Record<string, unknown>) => {
            const entries = Object.entries(obj).filter(([, val]) => val != null);
            if (!entries.length) return null;
            return (
              <div
                style={{ display: "flex", flexWrap: "wrap", gap: ".35rem", marginTop: ".25rem" }}
              >
                {entries.map(([k, val]) => (
                  <span
                    key={k}
                    style={{
                      background: "#3a3a3a",
                      padding: ".2rem .5rem",
                      borderRadius: 4,
                      fontSize: ".6rem",
                    }}
                  >
                    {k}: {String(val)}
                  </span>
                ))}
              </div>
            );
          };

          return (
            <li
              key={v.id}
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
                <h2 style={{ margin: 0 }}>{v.en?.title || v.es?.title || v.id}</h2>
                <code style={{ fontSize: ".7rem", opacity: 0.75 }}>{v.id}</code>
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
                {v.en && (
                  <div style={{ flex: 1, minWidth: 280 }}>
                    <h3 style={{ margin: ".25rem 0 .3rem" }}>EN</h3>
                    <p style={{ margin: 0, fontSize: ".8rem", fontWeight: 600 }}>
                      {v.en.description}
                    </p>
                    <div style={{ fontSize: ".7rem", lineHeight: 1.35, marginTop: ".5rem" }}>
                      <p style={{ margin: "0 0 .35rem" }}>
                        <strong>Impact:</strong> {v.en.impact}
                      </p>
                      <p style={{ margin: "0 0 .35rem" }}>
                        <strong>Threat:</strong> {v.en.threat}
                      </p>
                      <p style={{ margin: 0 }}>
                        <strong>Recommendation:</strong> {v.en.recommendation}
                      </p>
                    </div>
                  </div>
                )}
                {v.es && (
                  <div style={{ flex: 1, minWidth: 280 }}>
                    <h3 style={{ margin: ".25rem 0 .3rem" }}>ES</h3>
                    <p style={{ margin: 0, fontSize: ".8rem", fontWeight: 600 }}>
                      {v.es.description}
                    </p>
                    <div style={{ fontSize: ".7rem", lineHeight: 1.35, marginTop: ".5rem" }}>
                      <p style={{ margin: "0 0 .35rem" }}>
                        <strong>Impact:</strong> {v.es.impact}
                      </p>
                      <p style={{ margin: "0 0 .35rem" }}>
                        <strong>Threat:</strong> {v.es.threat}
                      </p>
                      <p style={{ margin: 0 }}>
                        <strong>Recommendation:</strong> {v.es.recommendation}
                      </p>
                    </div>
                  </div>
                )}
              </div>
              {v.examples && (v.examples.non_compliant || v.examples.compliant) && (
                <details style={{ marginTop: ".6rem" }}>
                  <summary style={{ cursor: "pointer", fontSize: ".7rem", fontWeight: 600 }}>
                    Code Examples
                  </summary>
                  <div
                    style={{ display: "flex", flexWrap: "wrap", gap: "1rem", marginTop: ".5rem" }}
                  >
                    {v.examples.non_compliant && (
                      <div style={{ flex: 1, minWidth: 280 }}>
                        <div
                          style={{
                            fontSize: ".65rem",
                            fontWeight: 600,
                            opacity: 0.8,
                            marginBottom: ".25rem",
                          }}
                        >
                          Non-Compliant
                        </div>
                        <pre
                          style={{
                            background: "#1e1e1e",
                            padding: ".5rem",
                            borderRadius: 6,
                            fontSize: ".6rem",
                            overflowX: "auto",
                          }}
                        >
                          <code>{v.examples.non_compliant}</code>
                        </pre>
                      </div>
                    )}
                    {v.examples.compliant && (
                      <div style={{ flex: 1, minWidth: 280 }}>
                        <div
                          style={{
                            fontSize: ".65rem",
                            fontWeight: 600,
                            opacity: 0.8,
                            marginBottom: ".25rem",
                          }}
                        >
                          Compliant
                        </div>
                        <pre
                          style={{
                            background: "#1e1e1e",
                            padding: ".5rem",
                            borderRadius: 6,
                            fontSize: ".6rem",
                            overflowX: "auto",
                          }}
                        >
                          <code>{v.examples.compliant}</code>
                        </pre>
                      </div>
                    )}
                  </div>
                </details>
              )}
              <div style={{ marginTop: ".7rem", display: "grid", gap: ".6rem" }}>
                {v.score &&
                  (Object.values(scoreBase).some(Boolean) ||
                    Object.values(scoreTemporal).some(Boolean)) && (
                    <details>
                      <summary style={{ cursor: "pointer", fontSize: ".65rem", fontWeight: 700 }}>
                        score
                      </summary>
                      <div style={{ marginTop: ".5rem", display: "grid", gap: ".6rem" }}>
                        {Object.keys(scoreBase).length > 0 && (
                          <div>
                            <div
                              style={{
                                fontSize: ".6rem",
                                fontWeight: 600,
                                opacity: 0.75,
                                textTransform: "uppercase",
                                letterSpacing: ".5px",
                              }}
                            >
                              base
                            </div>
                            {renderKVGroup(scoreBase as Record<string, unknown>)}
                          </div>
                        )}
                        {Object.keys(scoreTemporal).length > 0 && (
                          <div>
                            <div
                              style={{
                                fontSize: ".6rem",
                                fontWeight: 600,
                                opacity: 0.75,
                                textTransform: "uppercase",
                                letterSpacing: ".5px",
                              }}
                            >
                              temporal
                            </div>
                            {renderKVGroup(scoreTemporal as Record<string, unknown>)}
                          </div>
                        )}
                      </div>
                    </details>
                  )}
                {v.score_v4 &&
                  (Object.values(scoreV4Base).some(Boolean) ||
                    Object.values(scoreV4Threat).some(Boolean)) && (
                    <details>
                      <summary style={{ cursor: "pointer", fontSize: ".65rem", fontWeight: 700 }}>
                        score_v4
                      </summary>
                      <div style={{ marginTop: ".5rem", display: "grid", gap: ".6rem" }}>
                        {Object.keys(scoreV4Base).length > 0 && (
                          <div>
                            <div
                              style={{
                                fontSize: ".6rem",
                                fontWeight: 600,
                                opacity: 0.75,
                                textTransform: "uppercase",
                                letterSpacing: ".5px",
                              }}
                            >
                              base
                            </div>
                            {renderKVGroup(scoreV4Base as Record<string, unknown>)}
                          </div>
                        )}
                        {Object.keys(scoreV4Threat).length > 0 && (
                          <div>
                            <div
                              style={{
                                fontSize: ".6rem",
                                fontWeight: 600,
                                opacity: 0.75,
                                textTransform: "uppercase",
                                letterSpacing: ".5px",
                              }}
                            >
                              threat
                            </div>
                            {renderKVGroup(scoreV4Threat as Record<string, unknown>)}
                          </div>
                        )}
                      </div>
                    </details>
                  )}
              </div>
              <details style={{ marginTop: ".7rem" }}>
                <summary style={{ cursor: "pointer", fontSize: ".65rem", fontWeight: 700 }}>
                  metadata
                </summary>
                <div
                  style={{ marginTop: ".5rem", fontSize: ".6rem", display: "grid", gap: ".6rem" }}
                >
                  <div>
                    <strong>Metadata fields:</strong>
                    {metaEntries.length === 0 && (
                      <div style={{ opacity: 0.6, marginTop: ".25rem" }}>None</div>
                    )}
                    {metaEntries.length > 0 && (
                      <div style={{ marginTop: ".5rem", display: "grid", gap: ".5rem" }}>
                        {metaEntries.map(([k, val]) => {
                          let yamlText = "";
                          if (
                            typeof val === "string" &&
                            !val.includes("\n") &&
                            val.length < 60 &&
                            !val.match(/:\s/)
                          ) {
                            yamlText = `${val}`;
                          } else {
                            try {
                              const docObj = { [k]: val };
                              yamlText = yaml.dump(docObj, { lineWidth: 80 });
                              const firstColon = yamlText.indexOf(":");
                              if (firstColon !== -1)
                                yamlText = yamlText.slice(firstColon + 1).replace(/^\s*/, "");
                            } catch {
                              yamlText =
                                typeof val === "object"
                                  ? JSON.stringify(val, null, 2)
                                  : String(val);
                            }
                          }
                          const isBlock = /\n/.test(yamlText);
                          return (
                            <div
                              key={k}
                              style={{
                                background: "#2f2f2f",
                                padding: ".4rem .6rem",
                                borderRadius: 6,
                              }}
                            >
                              <div
                                style={{
                                  fontSize: ".55rem",
                                  fontWeight: 600,
                                  letterSpacing: ".5px",
                                  textTransform: "uppercase",
                                  opacity: 0.75,
                                }}
                              >
                                {k}
                              </div>
                              {isBlock ? (
                                <pre
                                  style={{
                                    margin: ".35rem 0 0",
                                    background: "#1e1e1e",
                                    padding: ".5rem",
                                    borderRadius: 6,
                                    whiteSpace: "pre-wrap",
                                    fontSize: ".55rem",
                                    maxHeight: 220,
                                    overflow: "auto",
                                  }}
                                >
                                  {yamlText}
                                </pre>
                              ) : (
                                <div
                                  style={{
                                    fontSize: ".6rem",
                                    marginTop: ".15rem",
                                    wordBreak: "break-word",
                                  }}
                                >
                                  {yamlText || <em style={{ opacity: 0.6 }}>empty</em>}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </div>
              </details>
              {v.requirements?.length ? (
                <div style={{ marginTop: ".7rem" }}>
                  <strong style={{ fontSize: ".6rem", opacity: 0.8, marginRight: ".4rem" }}>
                    Requirements:
                  </strong>
                  <div
                    style={{
                      display: "inline-flex",
                      flexWrap: "wrap",
                      gap: ".35rem",
                      verticalAlign: "middle",
                    }}
                  >
                    {v.requirements.map((reqId) => (
                      <span
                        key={reqId}
                        style={{
                          background: "#3a3a3a",
                          padding: ".18rem .55rem",
                          borderRadius: 4,
                          fontSize: ".55rem",
                        }}
                      >
                        {reqId}
                      </span>
                    ))}
                  </div>
                </div>
              ) : null}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
