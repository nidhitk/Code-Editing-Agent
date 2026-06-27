from pathlib import Path

from utils.helpers import read_file, write_file
from ast_engine.patcher import apply_patch
from runner.rollback import create_backup
from runner.diff_viewer import generate_diff
from ast_engine.project_index import choose_best_definition, collect_impacted_files
from ast_engine.project_index import build_python_index


def _resolve_target_path(project_path, file_path):
    target = Path(file_path)

    if target.is_absolute():
        return target.resolve()

    project_root = Path(project_path).resolve()
    project_name = Path(project_path)

    if target.parts[: len(project_root.parts)] == project_root.parts:
        return target.resolve()

    if target.parts[: len(project_name.parts)] == project_name.parts:
        return target.resolve()

    return (project_root / target).resolve()


def editor_agent(state):
    plan = state["edit_plan"]
    requirement = state["requirement"]
    project_path = state["project_path"]
    project_summary = state.get("project_summary", {})

    generated_changes = []

    for step in plan:
        file_path = step.get("file")

        if not file_path:
            continue

        target_path = _resolve_target_path(project_path, file_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        original_code = ""
        if target_path.exists():
            original_code = read_file(str(target_path))

        create_backup(str(target_path))

        snippet_context = None
        if target_path.suffix == ".py" and step["action"] in {"rewrite_logic", "modify_function", "add_class"}:
            best_definition = choose_best_definition(
                requirement,
                str(target_path),
                state.get("project_summary", {}).get("ast_metadata", {}),
                original_code if original_code else None
            )
            snippet_context = best_definition or None

        updated_code = apply_patch(
            original_code,
            step,
            requirement,
            context=snippet_context
        )

        diff = generate_diff(
            original_code,
            updated_code,
            str(target_path)
        )

        write_file(str(target_path), updated_code)

        generated_changes.append({
            "file": str(target_path),
            "action": step["action"],
            "diff": diff
        })

    changed_files = [change["file"] for change in generated_changes]
    if changed_files:
        refreshed_index = build_python_index(project_path, state.get("affected_files", []))
        project_summary = {**project_summary, **refreshed_index}
        impacted_files = collect_impacted_files(changed_files, project_summary)

        for impacted_path in impacted_files:
            impacted_target = Path(impacted_path)
            if not impacted_target.exists() or impacted_target.suffix != ".py":
                continue

            if impacted_path in changed_files:
                continue

            impacted_original = read_file(impacted_path)
            create_backup(impacted_path)

            impacted_definition = choose_best_definition(
                requirement,
                impacted_path,
                project_summary.get("ast_metadata", {}),
                impacted_original
            )

            dependency_requirement = (
                f"{requirement}\n\n"
                f"Primary changes:\n"
                f"{generated_changes}\n\n"
                f"Update the dependent file so it remains compatible with the primary change."
            )

            impacted_updated = apply_patch(
                impacted_original,
                {"action": "rewrite_logic", "file": impacted_path},
                dependency_requirement,
                context=impacted_definition
            )

            if impacted_updated == impacted_original:
                continue

            impacted_diff = generate_diff(
                impacted_original,
                impacted_updated,
                impacted_path
            )
            write_file(impacted_path, impacted_updated)

            generated_changes.append({
                "file": impacted_path,
                "action": "dependency_repair",
                "diff": impacted_diff
            })

    state["generated_changes"] = generated_changes
    return state
