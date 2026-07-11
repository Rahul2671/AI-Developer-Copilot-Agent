import {useState} from "react";
import {askQuestion, clearChatMemory} from "../api/api";

function Chat({projectId}){
const [question,setQuestion]=useState("");
const [answer,setAnswer]=useState("");
const [sources,setSources]=useState([]);
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
const res=await askQuestion({
project_id: projectId,
message: question
});
setAnswer(res.answer);
setSources(res.sources || []);
}catch(err){
console.log(err);
setAnswer("Something went wrong asking the codebase. Check the backend logs.");
setSources([]);
}finally{
setLoading(false);
}
}

const newConversation=async()=>{
if(!projectId){
return;
}
try{
await clearChatMemory(projectId);
}catch(err){
console.log(err);
}
setQuestion("");
setAnswer("");
setSources([]);
}

return (
<div>
<h2>Chat with your code</h2>
<textarea
placeholder="e.g. where is authentication handled?"
value={question}
onChange={
e=>setQuestion(e.target.value)
}
/>
<div className="ask-row">
<button onClick={send} disabled={loading}>
{loading ? "Thinking..." : "Ask"}
</button>
<button onClick={newConversation} disabled={loading} style={{marginLeft:"8px"}}>
New conversation
</button>
</div>
{answer && (
<div className="answer-block">
<p className="answer-label">Answer</p>
<p className="answer-text">{answer}</p>

{sources.length > 0 && (
<div className="sources-block">
<p className="sources-label">Sources</p>
<ul className="sources-list">
{sources.map((s, i) => (
<li key={i} className="source-item">
<span className="source-file">{s.file}</span>
<span className="source-lines"> Lines {s.start_line}-{s.end_line}</span>
{s.symbol && (
<span className="source-symbol"> · {s.kind} {s.symbol}</span>
)}
</li>
))}
</ul>
</div>
)}
</div>
)}
</div>
)
}
export default Chat;
