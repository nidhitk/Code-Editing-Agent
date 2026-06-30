import difflib
import html
from pathlib import Path


RED = "\033[31m"
GREEN = "\033[32m"
CYAN = "\033[36m"
RESET = "\033[0m"


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


def colorize_diff(diff_text):
    colored_lines = []

    for line in diff_text.splitlines():
        if line.startswith("---") or line.startswith("+++"):
            colored_lines.append(f"{CYAN}{line}{RESET}")
        elif line.startswith("+") and not line.startswith("+++"):
            colored_lines.append(f"{GREEN}{line}{RESET}")
        elif line.startswith("-") and not line.startswith("---"):
            colored_lines.append(f"{RED}{line}{RESET}")
        else:
            colored_lines.append(line)

    return "\n".join(colored_lines)


def render_html_diff(diff_text, title="Code Diff"):
    rows = []

    for line in diff_text.splitlines():
        if line.startswith("---") or line.startswith("+++"):
            cls = "header"
        elif line.startswith("+") and not line.startswith("+++"):
            cls = "add"
        elif line.startswith("-") and not line.startswith("---"):
            cls = "remove"
        else:
            cls = "context"

        rows.append(
            f'<div class="line {cls}"><pre>{html.escape(line)}</pre></div>'
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>
    body {{
      margin: 0;
      padding: 24px;
      background: #0f1115;
      color: #e6e6e6;
      font-family: Consolas, "Courier New", monospace;
    }}
    h1 {{
      font-size: 18px;
      margin: 0 0 16px;
      color: #f5f5f5;
    }}
    .diff {{
      border: 1px solid #2a2f3a;
      border-radius: 10px;
      overflow: hidden;
    }}
    .line pre {{
      margin: 0;
      padding: 6px 12px;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .header {{
      background: #1d2330;
      color: #8fb4ff;
    }}
    .add {{
      background: rgba(46, 160, 67, 0.18);
      color: #7ee787;
    }}
    .remove {{
      background: rgba(248, 81, 73, 0.18);
      color: #ff7b72;
    }}
    .context {{
      background: #0f1115;
      color: #d0d7de;
    }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <div class="diff">
    {''.join(rows)}
  </div>
</body>
</html>
"""


def write_diff_report(project_path, generated_changes, filename="codex_review.html"):
    project_root = Path(project_path).resolve()
    report_dir = project_root / ".codex-review"
    report_dir.mkdir(parents=True, exist_ok=True)

    sections = []
    for change in generated_changes:
        sections.append(
            render_html_diff(
                change["diff"],
                title=f'{change["file"]} - {change["action"]}'
            )
        )

    report_path = report_dir / filename
    report_path.write_text("\n<hr/>\n".join(sections), encoding="utf-8")
    return str(report_path)
