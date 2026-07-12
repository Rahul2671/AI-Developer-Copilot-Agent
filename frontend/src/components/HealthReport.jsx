import {useState} from "react";
import axios from "axios";

const API = axios.create({
    baseURL:"http://127.0.0.1:8000"
});

function HealthReport({projectId}){
const [report,setReport]=useState(null);
const [loading,setLoading]=useState(false);

const checkHealth=async()=>{
if(!projectId){
alert("Please upload a repo first");
return;
}
setLoading(true);
const res = await API.get(`/health/${projectId}`);
setReport(res.data);
setLoading(false);
}

return (
<div>
<h2>Project health report</h2>
<button onClick={checkHealth}>
{loading ? "Analyzing..." : "Run health check"}
</button>

{report && (
<div className="answer-block">
<p className="answer-label">Tech Stack</p>
<p className="answer-text">{report.tech_stack.join(", ") || "Unknown"}</p>

<p className="answer-label" style={{marginTop:"20px"}}>Total Files</p>
<p className="answer-text">{report.total_files}</p>

<p className="answer-label" style={{marginTop:"20px"}}>Tests</p>
<p className="answer-text">
{report.has_tests ? "✓ Test files found" : `⚠ ${report.missing_tests_warning}`}
</p>

<p className="answer-label" style={{marginTop:"20px"}}>
Security Warnings ({report.security_issue_count})
</p>
{report.security_warnings.length === 0 ? (
<p className="answer-text">No issues detected</p>
) : (
report.security_warnings.map((w, i) => (
<p className="answer-text" key={i}>⚠ {w.file}: {w.issue}</p>
))
)}

{report.dependencies && (
<>
<p className="answer-label" style={{marginTop:"20px"}}>Dependencies</p>
<p className="answer-text">
Python: {report.dependencies.python_packages.join(", ") || "None"}
</p>
<p className="answer-text">
npm: {report.dependencies.npm_packages.join(", ") || "None"}
</p>
{report.dependencies.heavy_dependencies.length > 0 && (
<p className="answer-text">
⚠ Heavy dependencies: {report.dependencies.heavy_dependencies.join(", ")}
</p>
)}
</>
)}

{report.unused_imports && report.unused_imports.length > 0 && (
<>
<p className="answer-label" style={{marginTop:"20px"}}>
Unused Imports ({report.unused_imports.length})
</p>
{report.unused_imports.map((u, i) => (
<p className="answer-text" key={i}>⚠ {u.file}: {u.unused_import}</p>
))}
</>
)}

{report.circular_imports && report.circular_imports.length > 0 && (
<>
<p className="answer-label" style={{marginTop:"20px"}}>
Circular Imports ({report.circular_imports.length})
</p>
{report.circular_imports.map((cycle, i) => (
<p className="answer-text" key={i}>⚠ {cycle.join(" → ")}</p>
))}
</>
)}

{report.entry_points && report.entry_points.length > 0 && (
<>
<p className="answer-label" style={{marginTop:"20px"}}>Entry Points</p>
<p className="answer-text">{report.entry_points.join(", ")}</p>
</>
)}
</div>
)}
</div>
)
}
export default HealthReport;