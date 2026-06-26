# ast_engine/patcher.py

def insert_import(code, import_stmt):
    lines = code.splitlines()

    insert_index = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith("import") or stripped.startswith("from"):
            insert_index = i + 1

    lines.insert(insert_index, import_stmt)

    return "\n".join(lines)


def insert_decorator(code, function_name, decorator):
    lines = code.splitlines()

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith(f"def {function_name}("):
            lines.insert(i, decorator)
            break

    return "\n".join(lines)


from core.llm import get_llm

llm = get_llm()


def rewrite_function(code, requirement):
    prompt = f"""
Rewrite code according to requirement.

Requirement:
{requirement}

Code:
{code}

Return only updated code.
"""

    response = llm.invoke(prompt)
    return response.content



def apply_patch(code, step, requirement):
    action = step["action"]

    if action == "insert_import":
        return insert_import(code, step["code"])

    elif action == "add_decorator":
        return insert_decorator(
            code,
            step["function"],
            step["decorator"]
        )

    elif action == "rewrite_logic":
        return rewrite_function(code, requirement)

    return code