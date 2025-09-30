import { useState } from "react";
import "./App.css";
import RequirementsPage from "./pages/RequirementsPage";
import CompliancePage from "./pages/CompliancePage";
import VulnerabilitiesPage from "./pages/VulnerabilitiesPage";
import SolutionsPage from "./pages/SolutionsPage";

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
      {view === "requirements" && <RequirementsPage />}
      {view === "compliance" && <CompliancePage />}
      {view === "vulnerabilities" && <VulnerabilitiesPage />}
      {view === "solutions" && <SolutionsPage />}
    </div>
  );
}

export default App;
