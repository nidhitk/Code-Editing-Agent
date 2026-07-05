from core.graph import build_graph
from runner.rollback import rollback_file
from runner.diff_viewer import colorize_diff, write_diff_report


def _build_initial_state(project_path, requirement):
    return {
        "requirement": requirement,
        "clarification_answer": "",
        "project_path": project_path,
        "clarification_needed": False,
        "clarification_question": "",
        "project_summary": {},
        "affected_files": [],
        "relevant_files": [],
        "dependency_files": [],
        "selected_snippets": {},
        "edit_plan": [],
        "generated_changes": [],
        "validation_status": "",
        "validation_attempts": 0,
        "validation_error": ""
    }


def _append_requirement(base_requirement, extra_requirement, label):
    extra_requirement = extra_requirement.strip()
    if not extra_requirement:
        return base_requirement

    return (
        f"{base_requirement}\n\n{label}: {extra_requirement}\n"
        "Treat the latest requirement as authoritative."
    )


def _rollback_session(session_files):
    for file_path in sorted(set(session_files)):
        rollback_file(file_path)


def run_cli():
    graph = build_graph()

    project_path = input("Project path: ")
    requirement = input("Requirement: ")
    current_requirement = requirement
    session_files = []

    while True:
        state = _build_initial_state(project_path, current_requirement)
        result = graph.invoke(state)

        for change in result.get("generated_changes", []):
            session_files.append(change["file"])

        if result["clarification_needed"]:
            print("\nNeed clarification:")
            print(result["clarification_question"])

            clarification_answer = input("Answer: ").strip()

            if not clarification_answer:
                print("No clarification answer provided. Stopping.")
                return

            current_requirement = _append_requirement(
                current_requirement,
                clarification_answer,
                "Clarification answer"
            )
            continue

        if result["validation_status"] != "pass":
            print("\nValidation failed:")
            print(result.get("validation_error") or "No validation details available.")

            choice = input("\nAdd another requirement and retry? (yes/no): ").strip().lower()
            if choice == "yes":
                extra_requirement = input("Additional requirement: ").strip()
                current_requirement = _append_requirement(
                    current_requirement,
                    extra_requirement,
                    "Additional requirement"
                )
                continue

            _rollback_session(session_files)
            print("Rollback complete.")
            return

        print("\nGenerated Changes:\n")

        for change in result["generated_changes"]:
            print("=" * 80)
            print(colorize_diff(change["diff"]))

        report_path = write_diff_report(project_path, result["generated_changes"])
        print(f"\nColored review report saved to: {report_path}")

        choice = input("\nChoose action: [a]ccept, [e]dit again, [r]ollback: ").strip().lower()

        if choice in {"e", "edit", "more"}:
            extra_requirement = input("Additional requirement: ").strip()
            current_requirement = _append_requirement(
                current_requirement,
                extra_requirement,
                "Additional requirement"
            )
            continue

        if choice in {"r", "rollback"}:
            _rollback_session(session_files)
            print("Rollback complete.")
            return

        print("Changes accepted.")
        return
