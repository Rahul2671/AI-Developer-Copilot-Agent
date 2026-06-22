import {useState} from "react";
import {askQuestion} from "../api/api";


function Chat(){

const [question,setQuestion]=useState("");
const [answer,setAnswer]=useState("");

const send=async()=>{


const res=await askQuestion({

project_id:"demo",

question

});


setAnswer(res.answer);


}



return (

<div>

<h2>Chat With Code</h2>


<textarea

value={question}

onChange={
e=>setQuestion(e.target.value)
}

/>


<br/>

<button onClick={send}>
Ask
</button>


<h3>Answer</h3>

<p>{answer}</p>


</div>

)

}


export default Chat;