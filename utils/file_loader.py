from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".java",
    ".ts"
}


def load_project_files(project_path):
    files = []

    root = Path(project_path)

    for file in root.rglob("*"):
        if file.suffix in SUPPORTED_EXTENSIONS:
            files.append(str(file))

    return files