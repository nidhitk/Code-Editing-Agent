from langgraph.graph import StateGraph, START, END
from core.state import AgentState

from agents.clarifier import clarifier_agent
from agents.analyzer import analyzer_agent
from agents.planner import planner_agent
from agents.editor import editor_agent
from agents.validator import validator_agent


def route_after_clarifier(state):
    if state["clarification_needed"]:
        return "ask_user"
    return "continue"


def route_after_validation(state):
    if state["validation_status"] == "pass":
        return "done"
    return "retry"


def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("clarifier", clarifier_agent)
    builder.add_node("analyzer", analyzer_agent)
    builder.add_node("planner", planner_agent)
    builder.add_node("editor", editor_agent)
    builder.add_node("validator", validator_agent)

    builder.add_edge(START, "clarifier")
    builder.add_edge("analyzer", "planner")
    builder.add_edge("planner", "editor")
    builder.add_edge("editor", "validator")

    builder.add_conditional_edges(
        "clarifier",
        route_after_clarifier,
        {
            "ask_user": END,
            "continue": "analyzer"
        }
    )

    builder.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "retry": "planner",
            "done": END
        }
    )

    return builder.compile()