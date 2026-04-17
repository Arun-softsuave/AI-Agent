#
import pandas as pd

def build_rich_schema(csv_path):
    df = pd.read_csv(csv_path)

    schema = f"""
Dataset Name: Global Sales Records

Purpose:
Contains international sales transactions including products,
countries, sales channels, dates, revenue, cost and profit.

Total Rows: {len(df)}
Total Columns: {len(df.columns)}

Columns:
"""

    descriptions = {
        "Region": "Geographic business region (Asia, Europe, Africa etc)",
        "Country": "Country where order was placed",
        "Item Type": "Product category sold",
        "Sales Channel": "Mode of sale: Online or Offline",
        "Order Priority": "Urgency level H/M/L/C",
        "Order Date": "Date order was created",
        "Order ID": "Unique order identifier",
        "Ship Date": "Date order shipped",
        "Units Sold": "Number of units sold",
        "Unit Price": "Selling price per unit",
        "Unit Cost": "Cost price per unit",
        "Total Revenue": "Total sales revenue",
        "Total Cost": "Total purchase/manufacturing cost",
        "Total Profit": "Revenue minus cost"
    }

    for col in df.columns:
        dtype = str(df[col].dtype)
        sample = df[col].dropna().astype(str).head(3).tolist()

        schema += f"""
{col}
- Type: {dtype}
- Meaning: {descriptions.get(col, 'Business column')}
- Sample Values: {sample}
"""

    return schema