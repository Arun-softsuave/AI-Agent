# import pandas as pd

# def execute_query(state):

#     df = pd.read_csv("data/sales.csv")

#     query = state["query"]

#     try:
#         result = eval(
#             query,
#             {"__builtins__": {}},
#             {"df": df, "pd": pd}
#         )

#         if hasattr(result, "to_dict"):
#             state["retrieved_data"] = result.to_dict(
#                 orient="records"
#             )
#         else:
#             state["retrieved_data"] = result

#     except Exception as e:
#         state["retrieved_data"] = f"Error: {str(e)}"

#     return state