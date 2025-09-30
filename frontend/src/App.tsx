import { useState, lazy, Suspense } from "react";
import "./App.css";

// Code-split page modules: they will be requested only when user navigates.
// Vite will emit separate chunks for each lazy import.
const RequirementsPage = lazy(() => import("./pages/RequirementsPage"));
const CompliancePage = lazy(() => import("./pages/CompliancePage"));
const VulnerabilitiesPage = lazy(() => import("./pages/VulnerabilitiesPage"));
const SolutionsPage = lazy(() => import("./pages/SolutionsPage"));

type View = "requirements" | "compliance" | "vulnerabilities" | "solutions";

function App() {
  const [view, setView] = useState<View>("requirements");

  return (
    <div>
      <nav style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem" }}>
        <button onClick={() => setView("requirements")} disabled={view === "requirements"}>
          Requirements
        </button>
        <button onClick={() => setView("compliance")} disabled={view === "compliance"}>
          Compliance
        </button>
        <button onClick={() => setView("vulnerabilities")} disabled={view === "vulnerabilities"}>
          Vulnerabilities
        </button>
        <button onClick={() => setView("solutions")} disabled={view === "solutions"}>
          Solutions
        </button>
      </nav>
      <Suspense
        fallback=
          {<div style={{ fontSize: ".9rem", opacity: 0.7 }}>
            Loading {view}...
          </div>}
      >
        {view === "requirements" && <RequirementsPage />}
        {view === "compliance" && <CompliancePage />}
        {view === "vulnerabilities" && <VulnerabilitiesPage />}
        {view === "solutions" && <SolutionsPage />}
      </Suspense>
    </div>
  );
}

export default App;
