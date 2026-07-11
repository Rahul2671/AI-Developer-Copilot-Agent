import {useState} from "react";
import {askWithTools} from "../api/api";

function ToolChat({projectId}){
const [question,setQuestion]=useState("");
const [answer,setAnswer]=useState("");
const [toolCalls,setToolCalls]=useState([]);
const [loading,setLoading]=useState(false);

const send=async()=>{
if(!projectId){
alert("Please upload a repo first");
return;
}
if(!question.trim()){
return;
}
setLoading(true);
try{
const res=await askWithTools({
project_id: projectId,
question: question
});
setAnswer(res.answer);
setToolCalls(res.tool_calls || []);
}catch(err){
console.log(err);
setAnswer("Something went wrong. Check the backend logs.");
setToolCalls([]);
}finally{
setLoading(false);
}
}

return (
<div>
<h2>Ask with tools (agent searches/reads files on its own)</h2>
<textarea
placeholder="e.g. find where projects get indexed, then check what happens if indexing fails"
value={question}
onChange={
e=>setQuestion(e.target.value)
}
/>
<div className="ask-row">
<button onClick={send} disabled={loading}>
{loading ? "Working..." : "Ask"}
</button>
</div>

{toolCalls.length > 0 && (
<div className="sources-block">
<p className="sources-label">Tool calls made ({toolCalls.length})</p>
<ul className="sources-list">
{toolCalls.map((t, i) => (
<li key={i} className="source-item">
<span className="source-file">{t.tool}</span>
<span className="source-lines"> {JSON.stringify(t.arguments)}</span>
</li>
))}
</ul>
</div>
)}

{answer && (
<div className="answer-block">
<p className="answer-label">Answer</p>
<p className="answer-text">{answer}</p>
</div>
)}
</div>
)
}
export default ToolChat;
