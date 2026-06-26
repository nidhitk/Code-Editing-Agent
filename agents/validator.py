import subprocess


def validator_agent(state):
    project_path = state["project_path"]

    try:
        result = subprocess.run(
            ["python", "-m", "compileall", project_path],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            state["validation_status"] = "pass"
        else:
            state["validation_status"] = "fail"

    except Exception:
        state["validation_status"] = "fail"

    return state