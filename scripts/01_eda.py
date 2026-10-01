import pandas as pd

df = pd.read_csv("ecommerce_customer_behavior_2026.csv")

# 1. How many actual buyers?
buyers = df["Completed_Orders"] > 0
print("Buyers:", buyers.sum(), f"({buyers.mean():.1%})")
print("Zero spend:", (df["Total_Spending_USD"] == 0).mean().round(3))
print("Buyers with zero spend:", (buyers & (df["Total_Spending_USD"] == 0)).sum())

# 2. What do the existing label columns look like?
for c in ["Customer_Segment", "Churn_Risk_Level", "Loyalty_Tier",
          "Purchase_Frequency", "Is_Active_Customer"]:
    print(f"\n{c}\n", df[c].value_counts())

# 3. Is churn circular with Recency? (the key check)
print(df.groupby("Churn_Risk_Level")[["Recency_Days", "Churn_Risk_Score",
      "Total_Orders", "Total_Spending_USD"]].mean().round(1))
print(df[["Churn_Risk_Score", "Recency_Days", "Total_Orders",
          "Total_Spending_USD", "Customer_Satisfaction_Score"]].corr().round(2))

# 4. What does "active" mean?
print(df.groupby("Is_Active_Customer")[["Recency_Days", "Total_Orders"]].mean().round(1))