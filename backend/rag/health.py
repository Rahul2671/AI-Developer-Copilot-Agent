import os
import re

TECH_STACK_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "React (JSX)",
    ".ts": "TypeScript",
    ".tsx": "React (TSX)",
    ".java": "Java",
    ".cpp": "C++",
}

SECURITY_PATTERNS = [
    (r"eval\(", "Use of eval() — can execute arbitrary code, high risk"),
    (r"password\s*=\s*[\"']", "Hardcoded password found in source code"),
    (r"api_key\s*=\s*[\"']", "Hardcoded API key found in source code"),
    (r"SELECT .* \+ ", "Possible SQL injection — string concatenation in query"),
]


def analyze_project(files_data):
    tech_stack = set()
    total_files = len(files_data)
    has_tests = False
    security_warnings = []

    for file in files_data:
        path = file["path"]
        content = file["content"]

        ext = os.path.splitext(path)[1]
        if ext in TECH_STACK_MAP:
            tech_stack.add(TECH_STACK_MAP[ext])

        filename = os.path.basename(path).lower()
        if "test" in filename or "spec" in filename:
            has_tests = True

        for pattern, message in SECURITY_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                security_warnings.append({
                    "file": path,
                    "issue": message
                })

    return {
        "total_files": total_files,
        "tech_stack": sorted(list(tech_stack)),
        "has_tests": has_tests,
        "missing_tests_warning": None if has_tests else "No test files detected in this project",
        "security_warnings": security_warnings,
        "security_issue_count": len(security_warnings)
    }