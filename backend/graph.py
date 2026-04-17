# =========================
# backend/graph.py
# =========================
from langgraph.graph import StateGraph, START, END

from backend.state import AgentState
from backend.memory import checkpointer

from backend.tracer import auto_trace

from backend.nodes import (
    understand_query,
    out_of_context,
    query_planner,
    generate_query,
    execute_query,
    retry_agent,
    generate_final_answer
)

from backend.conditional_node_check import (
    route_after_understand,
    route_after_validation,
    route_after_retry
)

builder = StateGraph(AgentState)

builder.add_node("Understand Query", auto_trace(understand_query))
builder.add_node("Out Of Context", auto_trace(out_of_context))
builder.add_node("Query Planner", auto_trace(query_planner))
builder.add_node("Generate Query", auto_trace(generate_query))
builder.add_node("Execute Query", auto_trace(execute_query))
builder.add_node("Retry Agent", auto_trace(retry_agent))
builder.add_node("Final Answer", auto_trace(generate_final_answer))

builder.add_edge(START, "Understand Query")

builder.add_conditional_edges(
    "Understand Query",
    route_after_understand,
    {
        "related": "Query Planner",
        "not_related": "Out Of Context"
    }
)

builder.add_edge("Query Planner", "Generate Query")
builder.add_edge("Generate Query", "Execute Query")

builder.add_conditional_edges(
    "Execute Query",
    route_after_validation,
    {
        "success": "Final Answer",
        "retry": "Retry Agent"
    }
)

builder.add_conditional_edges(
    "Retry Agent",
    route_after_retry,
    {
        "retry_again": "Execute Query",
        "fail": "Out Of Context"
    }
)

builder.add_edge("Final Answer", END)
builder.add_edge("Out Of Context", END)

graph = builder.compile(checkpointer=checkpointer)