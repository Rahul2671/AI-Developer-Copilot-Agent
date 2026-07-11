from rag.loader import extract_repo, read_code_files
from rag.chunker import chunk_files
from rag.vectorstore import add_chunks, search_chunks, search_by_file, list_indexed_files
from services.project_store import save_project, get_project


def index_project(project_id):
    folder = extract_repo(project_id)
    files_data = read_code_files(folder)
    chunks = chunk_files(files_data)
    add_chunks(project_id, chunks)
    save_project(project_id, {"indexed": True, "num_chunks": len(chunks)})
    return len(chunks)


def _require_indexed(project_id):
    project = get_project(project_id)
    if not project or not project.get("indexed"):
        raise ValueError(f"Project {project_id} is not indexed yet.")


def get_relevant_context(project_id, question, top_k=5):
    _require_indexed(project_id)

    results = search_chunks(project_id, question, top_k=top_k)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    chunks = []
    for text, meta in zip(documents, metadatas):
        chunks.append({
            "text": text,
            "source": meta["source"],
            "start_line": meta["start_line"],
            "end_line": meta["end_line"],
            "symbol": meta.get("symbol") or None,
            "kind": meta.get("kind"),
        })

    return chunks


def search_codebase(project_id, query, top_k=10):
    _require_indexed(project_id)

    results = search_chunks(project_id, query, top_k=top_k)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results.get("distances", [[None] * len(documents)])[0]

    matches = []
    for text, meta, distance in zip(documents, metadatas, distances):
        snippet = text if len(text) <= 300 else text[:300].rstrip() + "..."
        matches.append({
            "file": meta["source"],
            "start_line": meta["start_line"],
            "end_line": meta["end_line"],
            "symbol": meta.get("symbol") or None,
            "kind": meta.get("kind"),
            "snippet": snippet,
            "relevance": distance,
        })

    return matches


def get_file_chunks(project_id, file_path):
    _require_indexed(project_id)

    results = search_by_file(project_id, file_path)
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    chunks = [
        {
            "text": doc,
            "source": meta["source"],
            "start_line": meta["start_line"],
            "end_line": meta["end_line"],
            "symbol": meta.get("symbol") or None,
            "kind": meta.get("kind"),
        }
        for doc, meta in zip(documents, metadatas)
    ]
    chunks.sort(key=lambda c: c["start_line"])
    return chunks


def get_indexed_files(project_id):
    _require_indexed(project_id)
    return list_indexed_files(project_id)


from rag.health import analyze_project

def get_health_report(project_id, upload_path="data/projects"):
    extracted_folder = f"{upload_path}/{project_id}/extracted"
    files_data = read_code_files(extracted_folder)
    return analyze_project(files_data)