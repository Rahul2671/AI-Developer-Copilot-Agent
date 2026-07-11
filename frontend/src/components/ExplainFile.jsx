import {useState, useEffect} from "react";
import {listIndexedFiles, explainFile} from "../api/api";

function ExplainFile({projectId}){
const [files,setFiles]=useState([]);
const [selectedFile,setSelectedFile]=useState("");
const [explanation,setExplanation]=useState("");
const [loading,setLoading]=useState(false);

useEffect(()=>{
if(!projectId){
setFiles([]);
setSelectedFile("");
setExplanation("");
return;
}
listIndexedFiles(projectId)
.then(res=>setFiles(res.files || []))
.catch(err=>console.log(err));
}, [projectId]);

const runExplain=async()=>{
if(!projectId){
alert("Please upload a repo first");
return;
}
if(!selectedFile){
alert("Pick a file first");
return;
}
setLoading(true);
try{
const res=await explainFile({
project_id: projectId,
file_path: selectedFile
});
setExplanation(res.explanation);
}catch(err){
console.log(err);
setExplanation("Something went wrong explaining this file. Check the backend logs.");
}finally{
setLoading(false);
}
}

return (
<div>
<h2>Explain a file</h2>
<div className="upload-row">
<select
value={selectedFile}
onChange={e=>setSelectedFile(e.target.value)}
>
<option value="">Select a file...</option>
{files.map((f, i) => (
<option key={i} value={f}>{f}</option>
))}
</select>
<button onClick={runExplain} disabled={loading}>
{loading ? "Explaining..." : "Explain"}
</button>
</div>

{explanation && (
<div className="answer-block">
<p className="answer-label">Explanation</p>
<p className="answer-text">{explanation}</p>
</div>
)}
</div>
)
}
export default ExplainFile;