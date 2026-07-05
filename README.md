# Agentic Code Editor

An interactive Python CLI that uses a LangGraph workflow and an LLM to analyze a target project, plan code edits, apply patches, validate Python syntax, and present diffs for review.

The project is organized as a small multi-agent editing pipeline:

1. The user provides a project path and a natural-language requirement.
2. A clarifier decides whether the requirement needs more detail.
3. An analyzer scans supported source files and builds Python AST metadata.
4. A planner asks the LLM for a structured edit plan.
5. An editor applies the plan, creates backups, and generates diffs.
6. A validator compiles Python files and retries planning when validation fails.
7. The CLI lets the user accept, refine, or roll back the generated changes.

## Features

- Interactive CLI entry point with `python main.py`
- LangGraph-based workflow orchestration
- LLM-backed clarification, planning, and rewrite steps
- Project file discovery for `.py`, `.js`, `.java`, and `.ts` files
- Python AST indexing for symbols, imports, definitions, and dependency graphs
- Relevance scoring to choose likely files and snippets for an edit
- Backup creation before writing files
- Terminal unified diffs with ANSI colors
- HTML diff report generation under `.codex-review/`
- Rollback support for files changed during a CLI session
- Python syntax validation with `py_compile`

## Project Layout

```text
.
|-- main.py                  # CLI entry point
|-- requirements.txt         # Python dependencies
|-- agents/                  # LangGraph agent nodes
|   |-- analyzer.py          # Project scan, framework detection, AST indexing
|   |-- clarifier.py         # Requirement ambiguity check
|   |-- editor.py            # Applies edit plans and dependent-file repairs
|   |-- planner.py           # Produces JSON edit operations
|   `-- validator.py         # Python syntax validation
|-- ast_engine/              # Parsing, indexing, and patch helpers
|   |-- locator.py
|   |-- parser.py
|   |-- patcher.py
|   `-- project_index.py
|-- core/                    # Shared graph, state, and LLM setup
|   |-- graph.py
|   |-- llm.py
|   `-- state.py
|-- runner/                  # CLI support, rollback, and diff rendering
|   |-- cli.py
|   |-- diff_viewer.py
|   `-- rollback.py
|-- utils/                   # File loading and read/write helpers
|-- sample_project/          # Small FastAPI sample project
`-- pipeline_fence_test/     # Minimal test fixture project
```

## Requirements

- Python 3.10 or newer
- A Google Gemini API key for the active LLM configuration
- Dependencies from `requirements.txt`

The code currently imports both Groq and Google GenAI integrations, but `core/llm.py` is configured to use `ChatGoogleGenerativeAI`.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file in the repository root:

```env
GOOGLE_API_KEY=your_google_api_key
MODEL_NAME=gemini-1.5-flash
```

Use any `MODEL_NAME` supported by `langchain-google-genai` for your account. If you switch `core/llm.py` back to Groq, provide `GROQ_API_KEY` and a compatible Groq model instead.

## Usage

Start the CLI:

```powershell
python main.py
```

You will be prompted for:

- `Project path`: the project to edit, for example `sample_project`
- `Requirement`: the change you want, for example `Add a /users endpoint that returns a list of users`

After the workflow runs, the CLI prints generated diffs and writes an HTML review report to:

```text
<project>/.codex-review/codex_review.html
```

You can then choose:

- `a` or `accept`: keep the generated changes
- `e`, `edit`, or `more`: add another requirement and run the workflow again
- `r` or `rollback`: restore files from backups created during the session

If validation fails, the CLI allows you to provide an additional requirement and retry. If you decline, it rolls back the session changes.

## Generated Files

The tool may create these directories while running:

- `.backup/`: original file snapshots and sentinels used for rollback
- `.codex-cache/`: cached Python AST index data for scanned projects
- `.codex-review/`: generated HTML diff reports
- `__pycache__/`: Python bytecode from imports or validation

These are runtime artifacts and usually should not be committed.

## How Editing Works

The planner returns JSON operations such as:

- `insert_import`
- `modify_function`
- `create_file`
- `add_class`
- `rewrite_logic`

The editor resolves operation paths against the selected project, creates backups, and delegates code rewriting to the LLM. For Python files, it tries to replace the most relevant function or class definition using AST metadata before falling back to broader rewrites.

After primary edits, the editor uses the reverse dependency graph to find impacted Python files and may attempt dependent-file repairs.

## Current Limitations

- Validation only checks Python files with `py_compile`; JavaScript, TypeScript, and Java files are discovered but not compiled or tested.
- The strongest indexing and patching support is for Python.
- The workflow depends on LLM output quality. Invalid or incomplete plans may produce no changes or require another refinement pass.
- There is no automated test runner integration yet.
- Rollback uses backups in `.backup/` and is designed around files changed during the current CLI session.

## Development Notes

Useful commands:

```powershell
python main.py
python -m py_compile main.py
```

To run the sample flow, use `sample_project` as the project path when prompted.

When changing the workflow, start with:

- `core/graph.py` for agent routing
- `core/state.py` for shared state fields
- `agents/` for each pipeline stage
- `ast_engine/project_index.py` for relevance and dependency behavior
