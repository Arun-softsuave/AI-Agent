import pandas as pd
from backend.llm import get_llm
from backend.schema_builder import build_rich_schema

llm = get_llm()
CSV_PATH = "backend/data/sales.csv"


def get_recent_history(state, turns=2):
    messages = state.get("messages", [])

    limit = turns * 2
    recent = messages[-limit:]

    history = ""

    for msg in recent:
        role = msg["role"].upper()
        content = msg["content"]
        history += f"{role}: {content}\n"

    return history.strip()


# -----------------------------------
# 1. Understand Query
# -----------------------------------

def understand_query(state):
    schema = build_rich_schema(CSV_PATH)
    history = get_recent_history(state)

    prompt = f"""
You are an intelligent classifier.

Dataset:
{schema}

Previous Conversation:
{history}

Current User Question:
{state["user_query"]}

Use previous conversation if current question is short or incomplete.

Return ONLY YES if question can be answered from dataset.
Return ONLY NO if unrelated.

Examples:
Top profit country = YES
loss = YES (if previous was top profit country)
Who is Elon Musk = NO
How are you = NO
"""

    response = llm.invoke(prompt).content.strip().upper()

    state["csv_relevant"] = response.startswith("YES")
    state["retry_count"] = 0
    state["max_retry"] = 3

    state["messages"] = state.get("messages", []) + [
        {
            "role": "user",
            "content": state["user_query"]
        }
    ]

    return state


# -----------------------------------
# 2. Not Related
# -----------------------------------

def out_of_context(state):
    answer = "Sorry, your question is not available in the CSV dataset."

    state["final_answer"] = answer

    state["messages"] = state.get("messages", []) + [
        {
            "role": "assistant",
            "content": answer
        }
    ]

    return state


# -----------------------------------
# 3. Query Planner
# -----------------------------------

def query_planner(state):
    history = get_recent_history(state)

    prompt = f"""
Previous Conversation:
{history}

Current User Question:
{state["user_query"]}

Use previous context if needed.

Identify query type.

Return ONLY one word:

filter
aggregation
topn
comparison
trend
count
"""

    plan = llm.invoke(prompt).content.strip().lower()

    state["plan"] = plan

    return state


# -----------------------------------
# 4. Generate Query
# -----------------------------------

def generate_query(state):
    schema = build_rich_schema(CSV_PATH)
    history = get_recent_history(state)

    prompt = f"""
You are expert pandas analyst.

Dataset:
{schema}

Previous Conversation:
{history}

Current User Question:
{state["user_query"]}

Use previous context if question is incomplete.

Query Type:
{state["plan"]}

Rules:
1. Return ONLY pandas expression
2. dataframe name is df
3. No explanation
4. Use exact columns

Examples:

df.groupby("Country")["Total Profit"].sum().sort_values(ascending=False).head(5)

df.groupby("Country")["Total Profit"].sum().sort_values().head(5)
"""

    query = llm.invoke(prompt).content.strip()

    query = query.replace("```python", "").replace("```", "")

    state["query"] = query

    return state


# -----------------------------------
# 5. Execute Query
# -----------------------------------

def execute_query(state):
    import numpy as np

    df = pd.read_csv(CSV_PATH)

    try:
        result = eval(
            state["query"],
            {"__builtins__": {}},
            {"df": df, "pd": pd}
        )

        if hasattr(result, "empty") and result.empty:
            state["error"] = "Empty result"
            state["retrieved_data"] = None
            return state

        if hasattr(result, "to_dict"):
            state["retrieved_data"] = result.to_dict(
                orient="records"
            )

        elif isinstance(result, np.integer):
            state["retrieved_data"] = int(result)

        elif isinstance(result, np.floating):
            state["retrieved_data"] = float(result)

        elif isinstance(result, np.bool_):
            state["retrieved_data"] = bool(result)

        else:
            state["retrieved_data"] = result

        state["error"] = ""

    except Exception as e:
        state["error"] = str(e)
        state["retrieved_data"] = None

    return state


# -----------------------------------
# 6. Retry Agent
# -----------------------------------

def retry_agent(state):
    state["retry_count"] += 1

    schema = build_rich_schema(CSV_PATH)
    history = get_recent_history(state)

    prompt = f"""
You are pandas repair expert.

Dataset:
{schema}

Previous Conversation:
{history}

Current User Question:
{state["user_query"]}

Previous Failed Query:
{state["query"]}

Execution Error:
{state["error"]}

Use previous conversation if user query is incomplete.

Fix and return ONLY corrected pandas query.

Rules:
1. dataframe name is df
2. no explanation
3. exact columns only
"""

    fixed_query = llm.invoke(prompt).content.strip()

    fixed_query = fixed_query.replace("```python", "").replace("```", "")

    state["query"] = fixed_query

    return state


# -----------------------------------
# 7. Final Response
# -----------------------------------

def generate_final_answer(state):
    history = get_recent_history(state)

    prompt = f"""
You are business analyst.

Previous Conversation:
{history}

Current User Question:
{state["user_query"]}

Retrieved Data:
{state["retrieved_data"]}

Give clear human answer.
Use previous context if needed.
"""

    answer = llm.invoke(prompt).content.strip()

    state["final_answer"] = answer

    state["messages"] = state.get("messages", []) + [
        {
            "role": "assistant",
            "content": answer
        }
    ]

    return state