import {useState, useEffect} from "react";
import {listFolders, explainFolder} from "../api/api";

function FolderExplain({projectId}){
const [folders,setFolders]=useState([]);
const [selectedFolder,setSelectedFolder]=useState("");
const [explanation,setExplanation]=useState("");
const [loading,setLoading]=useState(false);

useEffect(()=>{
if(!projectId){
setFolders([]);
setSelectedFolder("");
setExplanation("");
return;
}
listFolders(projectId)
.then(res=>setFolders(res.folders || []))
.catch(err=>console.log(err));
}, [projectId]);

const runExplain=async()=>{
if(!projectId){
alert("Please upload a repo first");
return;
}
if(!selectedFolder){
alert("Pick a folder first");
return;
}
setLoading(true);
try{
const res=await explainFolder({
project_id: projectId,
folder_path: selectedFolder
});
setExplanation(res.explanation);
}catch(err){
console.log(err);
setExplanation("Something went wrong explaining this folder. Check backend logs.");
}finally{
setLoading(false);
}
}

return (
<div>
<h2>Explain a folder</h2>
<div className="upload-row">
<select
value={selectedFolder}
onChange={e=>setSelectedFolder(e.target.value)}
>
<option value="">Select a folder...</option>
{folders.map((f, i) => (
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
<p className="answer-text" style={{whiteSpace:"pre-line"}}>{explanation}</p>
</div>
)}
</div>
)
}
export default FolderExplain;