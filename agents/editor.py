from utils.helpers import read_file, write_file
from ast_engine.patcher import apply_patch
from runner.rollback import create_backup
from runner.diff_viewer import generate_diff


def editor_agent(state):
    plan = state["edit_plan"]
    requirement = state["requirement"]

    generated_changes = []

    for step in plan:
        file = step.get("file")

        if not file:
            continue

        original_code = read_file(file)

        create_backup(file)

        updated_code = apply_patch(
            original_code,
            step,
            requirement
        )

        diff = generate_diff(
            original_code,
            updated_code,
            file
        )

        write_file(file, updated_code)

        generated_changes.append({
            "file": file,
            "action": step["action"],
            "diff": diff
        })

    state["generated_changes"] = generated_changes
    return state