# from core.llm import get_llm


# def main():
#     llm = get_llm()

#     response = llm.invoke("Say hello from CodeEditAgent")
#     print(response.content)


# if __name__ == "__main__":
#     main()



# phase 2


from agents.clarifier import clarifier_agent
from agents.analyzer import analyzer_agent
from agents.planner import planner_agent
from agents.editor import editor_agent
from agents.validator import validator_agent


def main():
    state = {
        "requirement": "Add logging to FastAPI routes",
        "project_path": "./sample_project",
        "clarification_needed": False,
        "clarification_question": "",
        "project_summary": {},
        "affected_files": [],
        "edit_plan": [],
        "generated_changes": [],
        "validation_status": ""
    }

    state = clarifier_agent(state)
    print("Clarifier:", state)

    state = analyzer_agent(state)
    print("Analyzer:", state)

    state = planner_agent(state)
    print("Planner:", state)

    state = editor_agent(state)
    print("Editor:", state)

    state = validator_agent(state)
    print("Validator:", state)


if __name__ == "__main__":
    main()
