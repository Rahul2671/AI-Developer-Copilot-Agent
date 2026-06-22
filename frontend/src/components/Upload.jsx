import {useState} from "react";
import {uploadProject} from "../api/api";


function Upload(){

const [file,setFile]=useState(null);
const [status,setStatus]=useState("");

const upload=async()=>{

if(!file){
alert("Select zip file");
return;
}


try{

setStatus("Uploading...");

const res=await uploadProject(file);

console.log(res);

setStatus("Uploaded successfully");

}
catch(err){

console.log(err);
setStatus("Upload failed");

}

}



return (

<div>

<h2>Upload Repository</h2>

<input
type="file"
accept=".zip"
onChange={
e=>setFile(e.target.files[0])
}
/>

<button onClick={upload}>
Upload
</button>

<p>{status}</p>

</div>

)

}

export default Upload;