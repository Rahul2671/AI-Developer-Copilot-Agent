import {useState} from "react";
import {searchCodebase} from "../api/api";

function CodeSearch({projectId}){
const [query,setQuery]=useState("");
const [results,setResults]=useState([]);
const [loading,setLoading]=useState(false);
const [searched,setSearched]=useState(false);

const runSearch=async()=>{
if(!projectId){
alert("Please upload a repo first");
return;
}
if(!query.trim()){
return;
}
setLoading(true);
try{
const res=await searchCodebase({
project_id: projectId,
query: query,
top_k: 10
});
setResults(res.results || []);
setSearched(true);
}catch(err){
console.log(err);
setResults([]);
setSearched(true);
}finally{
setLoading(false);
}
}

return (
<div>
<h2>Search the codebase</h2>
<div className="upload-row">
<input
type="text"
placeholder="e.g. where is authentication implemented?"
value={query}
onChange={
e=>setQuery(e.target.value)
}
onKeyDown={
e=>{ if(e.key==="Enter") runSearch(); }
}
/>
<button onClick={runSearch} disabled={loading}>
{loading ? "Searching..." : "Search"}
</button>
</div>

{searched && results.length === 0 && (
<p className="status-text idle">No matches found.</p>
)}

{results.length > 0 && (
<div className="sources-block">
<p className="sources-label">Results</p>
<ul className="sources-list">
{results.map((r, i) => (
<li key={i} className="source-item">
<div>
<span className="source-file">{r.file}</span>
<span className="source-lines"> Lines {r.start_line}-{r.end_line}</span>
{r.symbol && (
<span className="source-symbol"> · {r.kind} {r.symbol}</span>
)}
</div>
<pre className="search-snippet">{r.snippet}</pre>
</li>
))}
</ul>
</div>
)}
</div>
)
}
export default CodeSearch;