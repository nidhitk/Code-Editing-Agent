from typing import TypedDict, List, Dict, Optional


class AgentState(TypedDict):
    requirement: str
    clarification_needed: bool
    clarification_question: str
    project_path: str
    project_summary: Dict
    affected_files: List[str]
    edit_plan: List[Dict]
    generated_changes: List[Dict]
    validation_status: str