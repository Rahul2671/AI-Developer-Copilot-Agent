import {useState} from "react";
import {askQuestion} from "../api/api";

function Chat({projectId}){
const [question,setQuestion]=useState("");
const [answer,setAnswer]=useState("");

const send=async()=>{
if(!projectId){
alert("Please upload a repo first");
return;
}
const res=await askQuestion({
project_id: projectId,
question
});
setAnswer(res.answer);
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
<button onClick={send}>Ask</button>
</div>
{answer && (
<div className="answer-block">
<p className="answer-label">Answer</p>
<p className="answer-text">{answer}</p>
</div>
)}
</div>
)
}
export default Chat;