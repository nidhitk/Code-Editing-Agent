import difflib


def generate_diff(old_code, new_code, filename):
    old_lines = old_code.splitlines()
    new_lines = new_code.splitlines()

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"{filename}_old",
        tofile=f"{filename}_new",
        lineterm=""
    )

    return "\n".join(diff)