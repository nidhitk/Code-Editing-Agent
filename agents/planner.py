import json
import re
from core.llm import get_llm


llm = get_llm()


def _extract_json(text):
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()
    return text.strip()


def _normalize_plan(content):
    try:
        parsed = json.loads(_extract_json(content))
    except json.JSONDecodeError:
        return []

    if isinstance(parsed, list):
        return parsed

    if isinstance(parsed, dict):
        if isinstance(parsed.get("operations"), list):
            return parsed["operations"]
        if isinstance(parsed.get("plan"), list):
            return parsed["plan"]

    return []


def planner_agent(state):
    requirement = state["requirement"]
    project_summary = state["project_summary"]
    validation_error = state.get("validation_error", "")
    files = project_summary.get("relevant_files") or project_summary.get("files", [])
    dependency_files = project_summary.get("dependency_files", [])
    selected_snippets = project_summary.get("selected_snippets", {})
    compact_project = {
        "framework": project_summary.get("framework", "unknown"),
        "relevant_files": files,
        "dependency_files": dependency_files,
        "selected_snippets": selected_snippets,
    }

    prompt = f"""
You are planning code edits.

Requirement:
{requirement}

Project:
{compact_project}

Available files:
{files}

Dependency files:
{dependency_files}

Relevant AST snippets:
{selected_snippets}

Validation errors from the previous attempt, if any:
{validation_error or "none"}

Return JSON list of operations.

Allowed actions:
- insert_import
- modify_function
- create_file
- add_class
- rewrite_logic

Each operation must include:
- action
- file
- code when inserting or creating content
- function and decorator for add_decorator
- when editing a Python function or class, return the full updated definition for that symbol

Pick files from the relevant files or dependency files and make the edit actually satisfy the requirement.
"""

    response = llm.invoke(prompt)
    plan = _normalize_plan(response.content)

    state["edit_plan"] = plan
    return state
