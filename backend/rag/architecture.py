import os
import re
import json

EXTENSION_STACK = {
    ".py": ("Languages", "Python"),
    ".js": ("Languages", "JavaScript"),
    ".jsx": ("Frontend", "React (JSX)"),
    ".ts": ("Languages", "TypeScript"),
    ".tsx": ("Frontend", "React (TSX)"),
    ".java": ("Languages", "Java"),
    ".cpp": ("Languages", "C++"),
    ".cc": ("Languages", "C++"),
    ".c": ("Languages", "C"),
    ".go": ("Languages", "Go"),
    ".rb": ("Languages", "Ruby"),
    ".rs": ("Languages", "Rust"),
    ".php": ("Languages", "PHP"),
    ".swift": ("Languages", "Swift"),
    ".kt": ("Languages", "Kotlin"),
    ".sql": ("Database", "SQL"),
    ".html": ("Frontend", "HTML"),
    ".css": ("Frontend", "CSS"),
    ".scss": ("Frontend", "SCSS"),
}

PACKAGE_KEYWORDS = {
    "fastapi": ("Backend", "FastAPI"),
    "flask": ("Backend", "Flask"),
    "django": ("Backend", "Django"),
    "express": ("Backend", "Express.js"),
    "react": ("Frontend", "React"),
    "vite": ("Frontend", "Vite"),
    "vue": ("Frontend", "Vue.js"),
    "next": ("Frontend", "Next.js"),
    "chromadb": ("Database", "ChromaDB (vector store)"),
    "pinecone": ("Database", "Pinecone (vector store)"),
    "mongodb": ("Database", "MongoDB"),
    "pymongo": ("Database", "MongoDB"),
    "postgres": ("Database", "PostgreSQL"),
    "psycopg2": ("Database", "PostgreSQL"),
    "mysql": ("Database", "MySQL"),
    "sqlite": ("Database", "SQLite"),
    "redis": ("Database", "Redis"),
    "groq": ("AI/ML", "Groq"),
    "openai": ("AI/ML", "OpenAI"),
    "anthropic": ("AI/ML", "Anthropic Claude"),
    "langchain": ("AI/ML", "LangChain"),
    "transformers": ("AI/ML", "HuggingFace Transformers"),
    "torch": ("AI/ML", "PyTorch"),
    "tensorflow": ("AI/ML", "TensorFlow"),
    "sklearn": ("AI/ML", "scikit-learn"),
    "docker": ("DevOps", "Docker"),
    "kubernetes": ("DevOps", "Kubernetes"),
    "pytest": ("Testing", "pytest"),
    "jest": ("Testing", "Jest"),
}

MANIFEST_FILENAMES = {
    "requirements.txt", "package.json", "pipfile", "pyproject.toml",
    "dockerfile", "docker-compose.yml", "docker-compose.yaml",
}


def build_tech_stack(files_data):
    stack = {}

    def add(category, name):
        stack.setdefault(category, set()).add(name)

    for file in files_data:
        path = file["path"]
        content = file["content"]
        ext = os.path.splitext(path)[1].lower()
        filename = os.path.basename(path).lower()

        if ext in EXTENSION_STACK:
            category, name = EXTENSION_STACK[ext]
            add(category, name)

        if filename in MANIFEST_FILENAMES:
            lowered = content.lower()
            for keyword, (category, name) in PACKAGE_KEYWORDS.items():
                if keyword in lowered:
                    add(category, name)

    return {category: sorted(names) for category, names in stack.items()}


def build_folder_summary(files_data):
    folders = {}
    for file in files_data:
        folder = os.path.dirname(file["path"]) or "."
        folders.setdefault(folder, []).append(os.path.basename(file["path"]))

    summary = []
    for folder in sorted(folders.keys()):
        summary.append({
            "folder": folder,
            "file_count": len(folders[folder]),
            "files": sorted(folders[folder]),
        })
    return summary


def detect_entry_points(files_data):
    entry_names = {
        "main.py", "app.py", "manage.py", "wsgi.py", "asgi.py",
        "index.js", "index.jsx", "index.ts", "index.tsx",
        "app.jsx", "app.tsx", "server.js", "server.ts",
    }
    entries = []
    for file in files_data:
        if os.path.basename(file["path"]).lower() in entry_names:
            entries.append(file["path"])
    return entries


HEAVY_PACKAGES = {
    "tensorflow", "torch", "opencv-python", "transformers", "pandas",
    "numpy", "scipy", "selenium", "playwright", "chromadb",
}


def _parse_requirements_txt(content):
    packages = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name = re.split(r"[<>=!~\[]", line)[0].strip()
        if name:
            packages.append(name.lower())
    return packages


def _parse_package_json(content):
    packages = []
    try:
        data = json.loads(content)
        for section in ("dependencies", "devDependencies"):
            packages.extend(data.get(section, {}).keys())
    except Exception:
        pass
    return [p.lower() for p in packages]


def analyze_dependencies(files_data):
    python_packages = []
    npm_packages = []

    for file in files_data:
        filename = os.path.basename(file["path"]).lower()
        if filename == "requirements.txt":
            python_packages.extend(_parse_requirements_txt(file["content"]))
        elif filename == "package.json":
            npm_packages.extend(_parse_package_json(file["content"]))

    all_packages = set(python_packages) | set(npm_packages)
    heavy = sorted(p for p in all_packages if p in HEAVY_PACKAGES)

    return {
        "python_packages": sorted(set(python_packages)),
        "npm_packages": sorted(set(npm_packages)),
        "heavy_dependencies": heavy,
    }


def detect_unused_imports(files_data):
    warnings = []
    for file in files_data:
        if not file["path"].endswith(".py"):
            continue
        content = file["content"]
        lines = content.splitlines()

        imported_names = []
        for line in lines:
            stripped = line.strip()
            match = re.match(r'^import\s+([\w\.]+)(?:\s+as\s+(\w+))?', stripped)
            if match:
                name = match.group(2) or match.group(1).split(".")[0]
                imported_names.append(name)
                continue
            match = re.match(r'^from\s+[\w\.]+\s+import\s+(.+)', stripped)
            if match:
                names = match.group(1).split(",")
                for n in names:
                    n = n.strip().split(" as ")[-1].strip()
                    if n and n != "*":
                        imported_names.append(n)

        body = "\n".join(
            l for l in lines
            if not re.match(r'^\s*(import|from)\s+', l)
        )

        for name in set(imported_names):
            if not re.search(r'\b' + re.escape(name) + r'\b', body):
                warnings.append({"file": file["path"], "unused_import": name})

    return warnings


def detect_circular_imports(files_data):
    module_map = {}
    for file in files_data:
        if file["path"].endswith(".py"):
            module_name = os.path.splitext(os.path.basename(file["path"]))[0]
            module_map[module_name] = file["path"]

    graph = {}
    for file in files_data:
        if not file["path"].endswith(".py"):
            continue
        imports = set()
        for line in file["content"].splitlines():
            match = re.match(r'^\s*from\s+([\w\.]+)\s+import', line) or re.match(r'^\s*import\s+([\w\.]+)', line)
            if match:
                first_part = match.group(1).split(".")[0]
                if first_part in module_map and module_map[first_part] != file["path"]:
                    imports.add(module_map[first_part])
        graph[file["path"]] = imports

    visited = set()
    stack = set()
    cycles = []

    def dfs(node, path):
        if node in stack:
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        stack.add(node)
        for neighbor in graph.get(node, []):
            dfs(neighbor, path + [neighbor])
        stack.discard(node)

    for node in graph:
        dfs(node, [node])

    unique_cycles = []
    seen = set()
    for cycle in cycles:
        key = frozenset(cycle)
        if key not in seen:
            seen.add(key)
            unique_cycles.append(cycle)

    return unique_cycles
