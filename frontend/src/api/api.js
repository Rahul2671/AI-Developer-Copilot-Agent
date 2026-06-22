import axios from "axios";

const API = axios.create({
    baseURL:"http://localhost:8000"
});


export const uploadProject = async(file)=>{

    const formData = new FormData();

    formData.append("file",file);

    const res = await API.post(
        "/upload",
        formData,
        {
            headers:{
                "Content-Type":"multipart/form-data"
            }
        }
    );

    return res.data;
}



export const askQuestion = async(data)=>{

    const res = await API.post(
        "/chat",
        data
    );

    return res.data;
}