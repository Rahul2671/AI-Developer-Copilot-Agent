import { useState, useEffect } from "react";

import Upload from "./components/Upload";
import Chat from "./components/Chat";
import HealthReport from "./components/HealthReport";
import ReviewCode from "./components/ReviewCode";
import AskBeforeCode from "./components/AskBeforeCode";
import CodeSearch from "./components/CodeSearch";
import ExplainFile from "./components/ExplainFile";
import ArchitectureSummary from "./components/ArchitectureSummary";
import FolderExplain from "./components/FolderExplain";
import ToolChat from "./components/ToolChat";

import "./App.css";

function App() {
  const [projectId, setProjectId] = useState(null);

  const [theme, setTheme] = useState(
    localStorage.getItem("theme") || "dark"
  );

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <div className="container">
      <header className="header">
        <div className="brand">
          <svg
            className="logo-mark"
            viewBox="0 0 40 40"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect
              x="1"
              y="1"
              width="38"
              height="38"
              rx="8"
              stroke="currentColor"
              strokeWidth="1.5"
            />
            <path
              d="M11 14L16 20L11 26"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <line
              x1="20"
              y1="26"
              x2="29"
              y2="26"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>

          <div>
            <h1>CodeSense</h1>
            <p className="subtitle">
              AI Developer Copilot • Understand • Search • Review • Plan
            </p>
          </div>
        </div>

        <button
          className="theme-toggle"
          onClick={() =>
            setTheme(theme === "dark" ? "light" : "dark")
          }
        >
          {theme === "dark" ? "☀️ Light" : "🌙 Dark"}
        </button>
      </header>

      <div className="card">
        <p className="card-label">01 • Upload Repository</p>
        <Upload onUploadSuccess={setProjectId} />
      </div>

      <div className="card">
        <p className="card-label">02 • Chat with Code</p>
        <Chat projectId={projectId} />
      </div>

      <div className="card">
        <p className="card-label">03 • Search Codebase</p>
        <CodeSearch projectId={projectId} />
      </div>

      <div className="card">
        <p className="card-label">04 • Explain File</p>
        <ExplainFile projectId={projectId} />
      </div>

      <div className="card">
        <p className="card-label">05 • Project Health</p>
        <HealthReport projectId={projectId} />
      </div>

      <div className="card">
        <p className="card-label">06 • Code Review</p>
        <ReviewCode projectId={projectId} />
      </div>

      <div className="card">
        <p className="card-label">07 • Ask Before Coding</p>
        <AskBeforeCode projectId={projectId} />
      </div>

      <div className="card">
        <p className="card-label">08 • Architecture Summary</p>
        <ArchitectureSummary projectId={projectId} />
      </div>

      <div className="card">
        <p className="card-label">09 • Explain Folder</p>
        <FolderExplain projectId={projectId} />
      </div>

      <div className="card">
        <p className="card-label">10 • AI Tool Mode</p>
        <ToolChat projectId={projectId} />
      </div>
    </div>
  );
}

export default App;