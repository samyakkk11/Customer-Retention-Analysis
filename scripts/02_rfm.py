import pandas as pd
import numpy as np

df = pd.read_csv("ecommerce_customer_behavior_2026.csv")
df = df.drop(columns=["Loyalty_Tier"])

buyers = df[df["Completed_Orders"] > 0].copy()

# Check the frequency distribution first (many ties expected)
print(buyers["Completed_Orders"].value_counts().sort_index().head(10))

# Recency: lower days = better, so reverse the labels
buyers["R"] = pd.qcut(buyers["Recency_Days"].rank(method="first"),
                      5, labels=[5, 4, 3, 2, 1]).astype(int)
buyers["F"] = pd.qcut(buyers["Completed_Orders"].rank(method="first"),
                      5, labels=[1, 2, 3, 4, 5]).astype(int)
buyers["M"] = pd.qcut(buyers["Total_Spending_USD"].rank(method="first"),
                      5, labels=[1, 2, 3, 4, 5]).astype(int)

R, F, M = buyers["R"], buyers["F"], buyers["M"]
conditions = [
    (R >= 4) & (F >= 4) & (M >= 4),   # Champions
    (R >= 3) & (F >= 3),              # Loyal
    (R >= 4) & (F <= 2),              # Promising
    (R <= 2) & (F >= 3),              # At-Risk
    (R <= 2) & (F <= 2),              # Lost
]
labels = ["Champions", "Loyal", "Promising", "At-Risk", "Lost"]
buyers["RFM_Segment"] = np.select(conditions, labels, default="Needs Attention")

# Summary table
summary = buyers.groupby("RFM_Segment").agg(
    customers=("Customer_ID", "count"),
    avg_recency=("Recency_Days", "mean"),
    avg_orders=("Completed_Orders", "mean"),
    avg_spend=("Total_Spending_USD", "mean"),
    total_revenue=("Total_Spending_USD", "sum"),
).round(1)
summary["pct_customers"] = (summary["customers"] / summary["customers"].sum() * 100).round(1)
summary["pct_revenue"] = (summary["total_revenue"] / summary["total_revenue"].sum() * 100).round(1)
print(summary.sort_values("total_revenue", ascending=False))

# Save for Power BI: buyers + non-buyers in one file
non_buyers = df[df["Completed_Orders"] == 0].copy()
non_buyers["RFM_Segment"] = "Never Purchased"
full = pd.concat([buyers, non_buyers], ignore_index=True)
full.to_csv("rfm_output.csv", index=False)
print(full["RFM_Segment"].value_counts())