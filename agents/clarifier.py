from core.llm import get_llm


llm = get_llm()


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

    clarification_needed = "yes" in content.lower()

    question = "none"
    if "QUESTION:" in content:
        question = content.split("QUESTION:")[-1].strip()

    state["clarification_needed"] = clarification_needed
    state["clarification_question"] = question

    return state