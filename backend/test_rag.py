from rag.retriever import index_project
from agents.code_agent import ask_codebase

num_chunks = index_project("test123")
print(f"Indexed {num_chunks} chunks")

result = ask_codebase("test123", "what does this project do?")
print("\nAnswer:", result["answer"])
print("\nSources:", result["sources"])