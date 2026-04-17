
from typing import TypedDict, Annotated, List, Dict, Any
import operator


class AgentState(TypedDict, total=False):
    thread_id: str
    user_query: str

    messages: Annotated[List[Dict[str, str]], operator.add]

    csv_relevant: bool
    intent: str
    plan: str

    query: str
    retrieved_data: Any
    final_answer: str

    error: str
    retry_count: int
    max_retry: int