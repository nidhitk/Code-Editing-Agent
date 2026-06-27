from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".java",
    ".ts"
}

EXCLUDED_DIRS = {
    ".git",
    ".backup",
    ".codex-cache",
    "__pycache__",
    "venv",
    ".venv",
    "node_modules"
}


def load_project_files(project_path):
    files = []

    root = Path(project_path).resolve()

    for file in root.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in file.parts):
            continue

        if file.is_file() and file.suffix in SUPPORTED_EXTENSIONS:
            files.append(str(file.resolve()))

    return sorted(files)
