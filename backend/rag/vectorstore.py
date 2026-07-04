import chromadb

client = chromadb.PersistentClient(path="data/vectorstore")


def get_collection(project_id):
    return client.get_or_create_collection(name=project_id)


def add_chunks(project_id, chunks):
    collection = get_collection(project_id)

    if not chunks:
        raise ValueError(
            "No supported source code files were found in the uploaded repository."
        )
    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"]} for c in chunks]
    )


def search_chunks(project_id, query, top_k=5):
    collection = get_collection(project_id)
    results = collection.query(query_texts=[query], n_results=top_k)
    return results