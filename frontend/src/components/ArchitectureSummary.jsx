import {useState} from "react";
import {getArchitectureSummary} from "../api/api";

function ArchitectureSummary({projectId}){
const [data,setData]=useState(null);
const [loading,setLoading]=useState(false);

const runSummary=async()=>{
if(!projectId){
alert("Please upload a repo first");
return;
}
setLoading(true);
try{
const res=await getArchitectureSummary(projectId);
setData(res);
}catch(err){
console.log(err);
setData({summary:"Something went wrong generating the architecture summary. Check backend logs."});
}finally{
setLoading(false);
}
}

return (
<div>
<h2>Architecture summary</h2>
<button onClick={runSummary} disabled={loading}>
{loading ? "Generating..." : "Generate architecture summary"}
</button>

{data && (
<div className="answer-block">
<p className="answer-label">Summary</p>
<p className="answer-text" style={{whiteSpace:"pre-line"}}>{data.summary}</p>

{data.tech_stack && (
<>
<p className="answer-label" style={{marginTop:"20px"}}>Tech Stack</p>
{Object.entries(data.tech_stack).map(([category, names], i) => (
<p className="answer-text" key={i}>{category}: {names.join(", ")}</p>
))}
</>
)}

{data.entry_points && data.entry_points.length > 0 && (
<>
<p className="answer-label" style={{marginTop:"20px"}}>Entry Points</p>
<p className="answer-text">{data.entry_points.join(", ")}</p>
</>
)}

{data.folder_summary && (
<>
<p className="answer-label" style={{marginTop:"20px"}}>Folders</p>
{data.folder_summary.map((f, i) => (
<p className="answer-text" key={i}>{f.folder}/ ({f.file_count} files)</p>
))}
</>
)}
</div>
)}
</div>
)
}
export default ArchitectureSummary;