import axios from "axios";

const API = axios.create({
    baseURL:"http://localhost:8002"
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


export const searchCodebase = async(data)=>{

    const res = await API.post(
        "/search",
        data
    );

    return res.data;
}


export const listIndexedFiles = async(projectId)=>{

    const res = await API.get(
        `/search/files/${projectId}`
    );

    return res.data;
}


export const explainFile = async(data)=>{

    const res = await API.post(
        "/explain",
        data
    );

    return res.data;
}
export const getArchitectureSummary = async(projectId)=>{

    const res = await API.get(
        `/architecture/summary/${projectId}`
    );

    return res.data;
}


export const listFolders = async(projectId)=>{

    const res = await API.get(
        `/architecture/folders/${projectId}`
    );

    return res.data;
}


export const explainFolder = async(data)=>{

    const res = await API.post(
        "/architecture/folder",
        data
    );

    return res.data;
}