import re

# ast_engine/patcher.py


def _strip_code_fences(text):
    if not text:
        return ""

    stripped = text.strip()

    fenced = re.search(r"```(?:[a-zA-Z0-9_+-]+)?\s*(.*?)\s*```", stripped, re.DOTALL)
    if fenced:
        return fenced.group(1).strip()

    lines = stripped.splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]

    return "\n".join(lines).strip()

def insert_import(code, import_stmt):
    lines = code.splitlines()

    insert_index = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith("import") or stripped.startswith("from"):
            insert_index = i + 1

    lines.insert(insert_index, import_stmt)

    return "\n".join(lines)


def create_file(code, file_contents):
    return _strip_code_fences(file_contents)


def replace_snippet(code, old_snippet, new_snippet):
    if not old_snippet:
        return new_snippet

    normalized_old = old_snippet.strip()
    normalized_new = _strip_code_fences(new_snippet)

    if normalized_old in code:
        return code.replace(normalized_old, normalized_new, 1)

    return None


def replace_python_definition(code, context, new_snippet):
    start_line = context.get("start_line")
    end_line = context.get("end_line")

    if not start_line or not end_line:
        return None

    lines = code.splitlines()
    updated_lines = lines[: start_line - 1]
    updated_lines.extend(_strip_code_fences(new_snippet).splitlines())
    updated_lines.extend(lines[end_line:])
    return "\n".join(updated_lines)


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


def rewrite_function(code, requirement, context=None):
    prompt_code = context if context else code
    prompt = f"""
Rewrite code according to requirement.

Requirement:
{requirement}

Code:
{prompt_code}

Return only updated code.
"""

    response = llm.invoke(prompt)
    return _strip_code_fences(response.content)



def apply_patch(code, step, requirement, context=None):
    action = step["action"]

    if action == "insert_import":
        return insert_import(code, step["code"])

    elif action == "create_file":
        return create_file(code, step.get("code", ""))

    elif action == "add_decorator":
        return insert_decorator(
            code,
            step["function"],
            step["decorator"]
        )

    elif action in {"rewrite_logic", "modify_function", "add_class"}:
        updated = rewrite_function(code, requirement, context=context)
        if isinstance(context, dict):
            replaced = replace_python_definition(code, context, updated)
            if replaced is not None:
                return replaced
            replaced = replace_snippet(code, context.get("snippet", ""), updated)
            if replaced is not None:
                return replaced
            return rewrite_function(code, requirement)
        if context:
            replaced = replace_snippet(code, context, updated)
            if replaced is not None:
                return replaced
            return rewrite_function(code, requirement)
        return updated

    return code
