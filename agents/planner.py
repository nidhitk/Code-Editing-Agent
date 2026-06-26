import json
from core.llm import get_llm


llm = get_llm()


def planner_agent(state):
    requirement = state["requirement"]
    project_summary = state["project_summary"]

    prompt = f"""
You are planning code edits.

Requirement:
{requirement}

Project:
{project_summary}

Return JSON list of operations.

Allowed actions:
- insert_import
- modify_function
- create_file
- add_class
- rewrite_logic
"""

    response = llm.invoke(prompt)

    try:
        plan = json.loads(response.content)
    except:
        plan = []

    state["edit_plan"] = plan
    return state