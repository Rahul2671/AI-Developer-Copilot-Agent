import {useState} from "react";
import {uploadProject} from "../api/api";

function Upload({onUploadSuccess}){
const [file,setFile]=useState(null);
const [status,setStatus]=useState("");
const [isIdle,setIsIdle]=useState(true);

const upload=async()=>{
if(!file){
alert("Select zip file");
return;
}
try{
setIsIdle(false);
setStatus("Uploading...");
const res=await uploadProject(file);
console.log(res);
setStatus(`Uploaded — Project ID: ${res.project_id}`);
onUploadSuccess(res.project_id);
}
catch(err){
console.log(err);
setStatus("Upload failed");
}
}

return (
<div>
<h2>Upload repository</h2>
<div className="upload-row">
<input
type="file"
accept=".zip"
onChange={
e=>setFile(e.target.files[0])
}
/>
<button onClick={upload}>Upload</button>
</div>
{status && <p className={`status-text ${isIdle ? "idle" : ""}`}>{status}</p>}
</div>
)
}
export default Upload;