from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict, total=False):
    thread_id: str
    user_query: str

    messages: List[Dict[str, str]]

    csv_relevant: bool
    plan: str

    query: str
    retrieved_data: Any
    final_answer: str

    error: str
    retry_count: int
    max_retry: int