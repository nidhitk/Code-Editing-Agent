from typing import TypedDict, List, Dict, Optional


class AgentState(TypedDict):
    requirement: str
    clarification_answer: str
    clarification_needed: bool
    clarification_question: str
    project_path: str
    project_summary: Dict
    affected_files: List[str]
    relevant_files: List[str]
    dependency_files: List[str]
    selected_snippets: Dict
    edit_plan: List[Dict]
    generated_changes: List[Dict]
    validation_status: str
    validation_attempts: int
    validation_error: str
