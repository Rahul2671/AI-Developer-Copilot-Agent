from rag.loader import extract_repo, read_code_files
from rag.chunker import chunk_files
from rag.vectorstore import add_chunks, search_chunks
from services.project_store import save_project, get_project


def index_project(project_id):
    folder = extract_repo(project_id)
    files_data = read_code_files(folder)
    chunks = chunk_files(files_data)
    add_chunks(project_id, chunks)
    save_project(project_id, {"indexed": True, "num_chunks": len(chunks)})
    return len(chunks)


def get_relevant_context(project_id, question):
    project = get_project(project_id)
    if not project or not project.get("indexed"):
        raise ValueError(f"Project {project_id} is not indexed yet.")

    results = search_chunks(project_id, question)
    contexts = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    return contexts, sources

from rag.health import analyze_project

def get_health_report(project_id, upload_path="data/projects"):
    extracted_folder = f"{upload_path}/{project_id}/extracted"
    files_data = read_code_files(extracted_folder)
    return analyze_project(files_data)