from core.graph import build_graph
from runner.rollback import rollback_file


def run_cli():
    graph = build_graph()

    project_path = input("Project path: ")
    requirement = input("Requirement: ")

    initial_state = {
        "requirement": requirement,
        "project_path": project_path,
        "clarification_needed": False,
        "clarification_question": "",
        "project_summary": {},
        "affected_files": [],
        "edit_plan": [],
        "generated_changes": [],
        "validation_status": ""
    }

    result = graph.invoke(initial_state)

    if result["clarification_needed"]:
        print("\nNeed clarification:")
        print(result["clarification_question"])
        return

    print("\nGenerated Changes:\n")

    for change in result["generated_changes"]:
        print("=" * 80)
        print(change["diff"])

    choice = input("\nAccept changes? (yes/no): ")

    if choice.lower() != "yes":
        for change in result["generated_changes"]:
            rollback_file(change["file"])

        print("Rollback complete.")
    else:
        print("Changes accepted.")