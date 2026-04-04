from langgraph.graph import StateGraph, END
from .nodes import extraction_node, analysis_node, critic_node
from src.core.agent_state import AgentState

def build_graph():
    """بناء LangGraph"""
    workflow = StateGraph(AgentState)

    workflow.add_node("extractor", extraction_node)
    workflow.add_node("analyst", analysis_node)
    workflow.add_node("critic", critic_node)

    workflow.set_entry_point("extractor")
    workflow.add_edge("extractor", "analyst")
    workflow.add_edge("analyst", "critic")
    workflow.add_edge("critic", END)

    return workflow.compile()
