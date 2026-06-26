from utils.helpers import read_file


def editor_agent(state):
    changes = []
    plan = state["edit_plan"]

    for step in plan:
        action = step.get("action")
        file = step.get("file")

        if not file:
            continue

        old_code = read_file(file)

        change = {
            "file": file,
            "action": action,
            "old_code": old_code
        }

        changes.append(change)

    state["generated_changes"] = changes
    return state