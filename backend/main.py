from fastapi import FastAPI
from pydantic import BaseModel

from backend.graph import graph

# MLflow imports
import mlflow
from backend.mlflow_config import *
from backend.tracer import trace_store

app = FastAPI()


class ChatRequest(BaseModel):
    thread_id: str
    message: str


@app.post("/chat")
def chat(req: ChatRequest):

    # Clear previous trace
    trace_store.clear()

    # Initial state
    state = {
        "thread_id": req.thread_id,
        "user_query": req.message
    }

    # Run graph
    result = graph.invoke(
        state,
        config={
            "configurable": {
                "thread_id": req.thread_id
            }
        }
    )

    # ---------------------------------
    # ADD MLflow HERE
    # ---------------------------------
    with mlflow.start_run(run_name="chat_request"):

        mlflow.log_param(
            "thread_id",
            req.thread_id
        )

        mlflow.log_param(
            "query",
            req.message
        )

        total = 0

        for step, data in trace_store.items():

            mlflow.log_metric(
                f"{step}_ms",
                data["latency_ms"]
            )

            total += data["latency_ms"]

        mlflow.log_metric(
            "total_latency_ms",
            total
        )

        mlflow.log_param(
            "retry_count",
            result.get("retry_count", 0)
        )

    # ---------------------------------
    # Return Answer
    # ---------------------------------
    return {
        "answer": result.get(
            "final_answer",
            "No answer generated"
        )
    }