from utils.file_loader import load_project_files
from utils.helpers import read_file
from ast_engine.project_index import (
    build_python_index,
    select_relevant_files,
    select_relevant_snippets,
)


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
    ast_index = build_python_index(project_path, files)
    file_contents = {}

    for file_path in files:
        try:
            file_contents[file_path] = read_file(file_path)
        except OSError:
            file_contents[file_path] = ""

    summary = {
        "framework": framework,
        "files": files,
        "file_contents": file_contents,
        "ast_metadata": ast_index["metadata"],
        "dependency_graph": ast_index["dependency_graph"],
        "reverse_dependency_graph": ast_index["reverse_dependency_graph"],
    }

    relevant_files, dependency_files = select_relevant_files(
        state["requirement"],
        summary
    )
    selected_snippets = select_relevant_snippets(
        state["requirement"],
        {
            **summary,
            "relevant_files": relevant_files,
            "dependency_files": dependency_files,
        }
    )

    summary["relevant_files"] = relevant_files
    summary["dependency_files"] = dependency_files
    summary["selected_snippets"] = selected_snippets

    state["project_summary"] = summary
    state["affected_files"] = files
    state["relevant_files"] = relevant_files
    state["dependency_files"] = dependency_files
    state["selected_snippets"] = selected_snippets

    return state
