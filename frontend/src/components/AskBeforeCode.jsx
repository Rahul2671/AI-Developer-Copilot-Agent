import {useState} from "react";
import axios from "axios";

const API = axios.create({
    baseURL:"http://127.0.0.1:8000"
});

function AskBeforeCode({projectId}){
const [request,setRequest]=useState("");
const [plan,setPlan]=useState(null);
const [loading,setLoading]=useState(false);

const analyze=async()=>{
if(!projectId){
alert("Please upload a repo first");
return;
}
if(!request){
alert("Describe the change you want to make");
return;
}
setLoading(true);
setPlan(null);
const res = await API.post("/plan/", {
project_id: projectId,
change_request: request
});
setPlan(res.data);
setLoading(false);
}

return (
<div>
<h2>Ask before you code</h2>
<textarea
placeholder="e.g. I want to add a payment gateway"
value={request}
onChange={e=>setRequest(e.target.value)}
/>
<div className="ask-row">
<button onClick={analyze}>
{loading ? "Analyzing impact..." : "Analyze change"}
</button>
</div>

{plan && !plan.error && (
<div className="answer-block">
<p className="answer-label">Summary</p>
<p className="answer-text">{plan.summary}</p>

<p className="answer-label" style={{marginTop:"20px"}}>Risk Level</p>
<p className="answer-text">{plan.risk_level} — Complexity: {plan.complexity_score}/10</p>

<p className="answer-label" style={{marginTop:"20px"}}>Affected Files</p>
{plan.affected_files?.map((f,i)=>(
<p className="answer-text" key={i}>• {f}</p>
))}

{plan.new_files_needed?.length > 0 && (
<>
<p className="answer-label" style={{marginTop:"20px"}}>New Files Needed</p>
{plan.new_files_needed.map((f,i)=>(
<p className="answer-text" key={i}>+ {f}</p>
))}
</>
)}

<p className="answer-label" style={{marginTop:"20px"}}>Required Changes</p>
{plan.required_changes?.map((c,i)=>(
<p className="answer-text" key={i}>{i+1}. {c}</p>
))}

<p className="answer-label" style={{marginTop:"20px"}}>Possible Breaking Points</p>
{plan.possible_breaking_points?.map((b,i)=>(
<p className="answer-text" key={i}>⚠ {b}</p>
))}
</div>
)}

{plan && plan.error && (
<div className="answer-block">
<p className="answer-text">⚠ {plan.error}</p>
</div>
)}
</div>
)
}
export default AskBeforeCode;
