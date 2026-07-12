import {useState, useEffect} from "react";
import axios from "axios";

const API = axios.create({
    baseURL:"http://127.0.0.1:8000"
});

function ReviewCode({projectId}){
const [files,setFiles]=useState([]);
const [selectedFile,setSelectedFile]=useState("");
const [review,setReview]=useState("");
const [loading,setLoading]=useState(false);

useEffect(()=>{
if(!projectId) return;
API.get(`/review/files/${projectId}`).then(res=>{
setFiles(res.data.files || []);
});
},[projectId]);

const runReview=async()=>{
if(!selectedFile){
alert("Select a file first");
return;
}
setLoading(true);
const res = await API.post("/review/", {
project_id: projectId,
file_path: selectedFile
});
setReview(res.data.review || res.data.error);
setLoading(false);
}

return (
<div>
<h2>Code review</h2>
{files.length === 0 ? (
<p className="status-text idle">Upload a repo first to see files here</p>
) : (
<div className="upload-row">
<select
value={selectedFile}
onChange={e=>setSelectedFile(e.target.value)}
style={{
flex:1,
minWidth:"180px",
background:"var(--bg-void)",
border:"1px solid var(--border-line)",
borderRadius:"6px",
color:"var(--text-primary)",
padding:"10px",
fontFamily:"'JetBrains Mono', monospace",
fontSize:"13px"
}}
>
<option value="">Select a file...</option>
{files.map((f,i)=>(
<option key={i} value={f}>{f}</option>
))}
</select>
<button onClick={runReview}>
{loading ? "Reviewing..." : "Review file"}
</button>
</div>
)}

{review && (
<div className="answer-block">
<p className="answer-label">Review</p>
<p className="answer-text">{review}</p>
</div>
)}
</div>
)
}
export default ReviewCode;
