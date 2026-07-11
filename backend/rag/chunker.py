import os
import re

MAX_CHUNK_LINES = 120
CHUNK_OVERLAP_LINES = 15
FALLBACK_LINES_PER_CHUNK = 40
FALLBACK_OVERLAP_LINES = 5

LANGUAGE_PATTERNS = {
    ".py": [
        (re.compile(r'^(\s*)class\s+([A-Za-z_]\w*)'), "class"),
        (re.compile(r'^(\s*)def\s+([A-Za-z_]\w*)'), "function"),
    ],
    ".js": [
        (re.compile(r'^(\s*)class\s+([A-Za-z_]\w*)'), "class"),
        (re.compile(r'^(\s*)function\s+([A-Za-z_]\w*)'), "function"),
        (re.compile(r'^(\s*)(?:export\s+)?(?:default\s+)?const\s+([A-Za-z_]\w*)\s*=\s*(?:async\s*)?\('), "function"),
    ],
    ".ts": [
        (re.compile(r'^(\s*)class\s+([A-Za-z_]\w*)'), "class"),
        (re.compile(r'^(\s*)function\s+([A-Za-z_]\w*)'), "function"),
        (re.compile(r'^(\s*)(?:export\s+)?(?:default\s+)?const\s+([A-Za-z_]\w*)\s*=\s*(?:async\s*)?\('), "function"),
    ],
    ".java": [
        (re.compile(r'^(\s*)(?:public|private|protected|final|abstract|\s)*class\s+([A-Za-z_]\w*)'), "class"),
        (re.compile(r'^(\s*)(?:public|private|protected|static|final|\s)+[\w<>\[\],\s]+?\s([A-Za-z_]\w*)\s*\([^;]*\)\s*\{'), "function"),
    ],
    ".go": [
        (re.compile(r'^(\s*)func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)'), "function"),
        (re.compile(r'^(\s*)type\s+([A-Za-z_]\w*)\s+struct'), "class"),
    ],
    ".rb": [
        (re.compile(r'^(\s*)class\s+([A-Za-z_]\w*)'), "class"),
        (re.compile(r'^(\s*)def\s+([A-Za-z_][\w?!]*)'), "function"),
    ],
}
LANGUAGE_PATTERNS[".jsx"] = LANGUAGE_PATTERNS[".js"]
LANGUAGE_PATTERNS[".tsx"] = LANGUAGE_PATTERNS[".ts"]
LANGUAGE_PATTERNS[".cs"] = LANGUAGE_PATTERNS[".java"]


def _find_boundaries(lines, ext):
    patterns = LANGUAGE_PATTERNS.get(ext)
    if not patterns:
        return None

    boundaries = []
    for i, line in enumerate(lines):
        for pattern, kind in patterns:
            match = pattern.match(line)
            if match:
                indent = len(match.group(1))
                name = match.group(2)
                boundaries.append({"line": i, "indent": indent, "kind": kind, "name": name})
                break
    return boundaries


def _qualified_name(boundary, class_stack):
    while class_stack and class_stack[-1]["indent"] >= boundary["indent"]:
        class_stack.pop()

    if boundary["kind"] == "class":
        full_name = boundary["name"]
        class_stack.append({"indent": boundary["indent"], "name": boundary["name"]})
    else:
        if class_stack:
            full_name = f"{class_stack[-1]['name']}.{boundary['name']}"
        else:
            full_name = boundary["name"]

    return full_name


def _split_oversized(start_line, end_line, symbol, kind, lines, source):
    total_lines = end_line - start_line
    if total_lines <= MAX_CHUNK_LINES:
        return [{
            "start_line": start_line + 1,
            "end_line": end_line,
            "symbol": symbol,
            "kind": kind,
        }]

    sub_chunks = []
    cursor = start_line
    while cursor < end_line:
        chunk_end = min(cursor + MAX_CHUNK_LINES, end_line)
        sub_chunks.append({
            "start_line": cursor + 1,
            "end_line": chunk_end,
            "symbol": symbol,
            "kind": kind,
        })
        if chunk_end >= end_line:
            break
        cursor = chunk_end - CHUNK_OVERLAP_LINES

    return sub_chunks


def _fallback_line_chunks(lines):
    ranges = []
    start = 0
    total = len(lines)
    while start < total:
        end = min(start + FALLBACK_LINES_PER_CHUNK, total)
        ranges.append({
            "start_line": start + 1,
            "end_line": end,
            "symbol": None,
            "kind": "block",
        })
        if end >= total:
            break
        start = end - FALLBACK_OVERLAP_LINES
    return ranges


def chunk_file_smart(file_entry):
    path = file_entry["path"]
    content = file_entry["content"]
    ext = os.path.splitext(path)[1].lower()
    lines = content.splitlines()

    if not lines:
        return []

    boundaries = _find_boundaries(lines, ext)
    ranges = []

    if not boundaries:
        ranges = _fallback_line_chunks(lines)
    else:
        class_stack = []

        if boundaries[0]["line"] > 0:
            ranges.append({
                "start_line": 1,
                "end_line": boundaries[0]["line"],
                "symbol": None,
                "kind": "module-level",
            })

        for idx, boundary in enumerate(boundaries):
            symbol = _qualified_name(boundary, class_stack)
            start_line = boundary["line"]
            end_line = boundaries[idx + 1]["line"] if idx + 1 < len(boundaries) else len(lines)
            ranges.extend(
                _split_oversized(start_line, end_line, symbol, boundary["kind"], lines, path)
            )

    chunks = []
    for r in ranges:
        text_lines = lines[r["start_line"] - 1: r["end_line"]]
        text = "\n".join(text_lines).strip()
        if not text:
            continue
        chunks.append({
            "id": f"{path}::{r['start_line']}-{r['end_line']}",
            "text": text,
            "source": path,
            "start_line": r["start_line"],
            "end_line": r["end_line"],
            "symbol": r["symbol"],
            "kind": r["kind"],
        })

    return chunks


def chunk_files(files_data):
    all_chunks = []
    for file_entry in files_data:
        all_chunks.extend(chunk_file_smart(file_entry))
    return all_chunks