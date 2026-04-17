
import pandas as pd
from backend.llm import get_llm
from backend.schema_builder import build_rich_schema



llm = get_llm()
CSV_PATH = "backend/data/sales.csv"


# -----------------------------------
# 1. Understand Query
# -----------------------------------

def understand_query(state):
    schema = build_rich_schema(CSV_PATH)

    prompt = f"""
You are an intelligent classifier.

Dataset:
{schema}

User Question:
{state["user_query"]}

Return ONLY YES if question can be answered from dataset.
Return ONLY NO if unrelated.

Examples:
Top profit country = YES
Total revenue by region = YES
Who is Elon Musk = NO
How are you = NO
"""

    response = llm.invoke(prompt).content.strip().upper()

    state["csv_relevant"] = response.startswith("YES")
    state["retry_count"] = 0
    state["max_retry"] = 3
    state["messages"] = state.get("messages", [])

    state["messages"].append(
        {
            "role": "user",
            "content": state["user_query"]
        }
    )

    return state


# -----------------------------------
# 2. Not Related
# -----------------------------------

def out_of_context(state):
    answer = "Sorry, your question is not available in the CSV dataset."

    state["final_answer"] = answer

    state["messages"].append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    return state


# -----------------------------------
# 3. Query Planner
# -----------------------------------

def query_planner(state):

    prompt = f"""
User Question:
{state["user_query"]}

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

    prompt = f"""
You are expert pandas analyst.

Dataset:
{schema}

User Question:
{state["user_query"]}

Query Type:
{state["plan"]}

Rules:
1. Return ONLY pandas expression
2. dataframe name is df
3. No explanation
4. Use exact columns

Examples:

df.groupby("Country")["Total Profit"].sum().sort_values(ascending=False).head(1)

df.groupby("Region")["Total Revenue"].sum().reset_index()
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

    prompt = f"""
You are pandas repair expert.

Dataset:
{schema}

User Question:
{state["user_query"]}

Previous Query:
{state["query"]}

Error:
{state["error"]}

Fix and return ONLY corrected pandas query.
Use dataframe name df.
"""

    fixed_query = llm.invoke(prompt).content.strip()

    fixed_query = fixed_query.replace("```python", "").replace("```", "")

    state["query"] = fixed_query

    return state


# -----------------------------------
# 7. Final Response
# -----------------------------------

def generate_final_answer(state):

    prompt = f"""
You are business analyst.

User Question:
{state["user_query"]}

Retrieved Data:
{state["retrieved_data"]}

Give clear human answer.
"""

    answer = llm.invoke(prompt).content.strip()

    state["final_answer"] = answer

    state["messages"].append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    return state