from typing import TypedDict, List
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    input: str
    chat_history: List[BaseMessage]
    context: str
    analysis: str
    dashboard_data: dict
    final_answer: str
    