def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def chunk_files(files_data):
    all_chunks = []
    for file in files_data:
        pieces = chunk_text(file["content"])
        for i, piece in enumerate(pieces):
            all_chunks.append({
                "id": f"{file['path']}_{i}",
                "text": piece,
                "source": file["path"]
            })
    return all_chunks