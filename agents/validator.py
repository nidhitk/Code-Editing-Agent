import py_compile

from utils.file_loader import load_project_files


def validator_agent(state):
    project_path = state["project_path"]
    py_files = [path for path in load_project_files(project_path) if path.endswith(".py")]
    state["validation_attempts"] = state.get("validation_attempts", 0) + 1

    errors = []

    for file_path in py_files:
        try:
            py_compile.compile(file_path, doraise=True)
        except Exception as exc:
            errors.append(f"{file_path}: {exc}")

    if errors:
        state["validation_status"] = "fail"
        state["validation_error"] = "\n".join(errors)
    else:
        state["validation_status"] = "pass"
        state["validation_error"] = ""

    return state
