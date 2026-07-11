import {useState} from "react";
import Upload from "./components/Upload";
import Chat from "./components/Chat";
import HealthReport from "./components/HealthReport";
import ReviewCode from "./components/ReviewCode";
import AskBeforeCode from "./components/AskBeforeCode";
import CodeSearch from "./components/CodeSearch";
import ExplainFile from "./components/ExplainFile";
import ArchitectureSummary from "./components/ArchitectureSummary";
import FolderExplain from "./components/FolderExplain";
import "./App.css";

function App() {
  const [projectId, setProjectId] = useState(null);

  return (
    <div className="container">
      <div className="header">
        <svg className="logo-mark" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="1" y="1" width="38" height="38" rx="8" stroke="#f0b429" strokeWidth="1.5"/>
          <path d="M11 14L16 20L11 26" stroke="#f0b429" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <line x1="20" y1="26" x2="29" y2="26" stroke="#f0b429" strokeWidth="2" strokeLinecap="round"/>
        </svg>
        <h1>CodeSense</h1>
      </div>
      <p className="subtitle">upload a repo, ask anything about the code!</p>

      <div className="card">
        <p className="card-label">Step 01</p>
        <Upload onUploadSuccess={setProjectId} />
      </div>

      <div className="card">
        <p className="card-label">Step 02</p>
        <Chat projectId={projectId} />
      </div>

      <div className="card">
        <p className="card-label">Step 03</p>
        <CodeSearch projectId={projectId} />
      </div>

      <div className="card">
        <p className="card-label">Step 04</p>
        <ExplainFile projectId={projectId} />
      </div>

      <div className="card">
        <p className="card-label">Step 05</p>
        <HealthReport projectId={projectId} />
      </div>

      <div className="card">
        <p className="card-label">Step 06</p>
        <ReviewCode projectId={projectId} />
      </div>

      <div className="card">
        <p className="card-label">Step 07</p>
        <AskBeforeCode projectId={projectId} />
      </div>
      <div className="card">
        <p className="card-label">Step 08</p>
        <ArchitectureSummary projectId={projectId} />
      </div>

      <div className="card">
        <p className="card-label">Step 09</p>
        <FolderExplain projectId={projectId} />
      </div>
    </div>
  )
}
export default App;