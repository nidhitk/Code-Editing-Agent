from core.llm import get_llm


llm = get_llm()


def _extract_flag(content, label):
    for line in content.splitlines():
        if line.strip().lower().startswith(f"{label.lower()}:"):
            return line.split(":", 1)[1].strip()
    return ""


def clarifier_agent(state):
    requirement = state["requirement"]

    prompt = f"""
You are a clarification agent.

Requirement:
{requirement}

Determine whether requirement is ambiguous.

Return ONLY in this format:
NEED_CLARIFICATION: yes/no
QUESTION: question or none
"""

    response = llm.invoke(prompt)
    content = response.content

    need_value = _extract_flag(content, "NEED_CLARIFICATION").lower()
    clarification_needed = need_value.startswith("y")

    question = _extract_flag(content, "QUESTION") or "none"

    state["clarification_needed"] = clarification_needed
    state["clarification_question"] = question

    return state
