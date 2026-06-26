from utils.file_loader import load_project_files
from utils.helpers import read_file


def detect_framework(files):
    framework = "unknown"

    for file in files:
        content = read_file(file)

        if "FastAPI" in content:
            return "FastAPI"

        if "Flask" in content:
            return "Flask"

        if "@SpringBootApplication" in content:
            return "Spring Boot"

        if "express()" in content:
            return "Express"

    return framework


def analyzer_agent(state):
    project_path = state["project_path"]

    files = load_project_files(project_path)
    framework = detect_framework(files)

    summary = {
        "framework": framework,
        "files": files
    }

    state["project_summary"] = summary

    return state