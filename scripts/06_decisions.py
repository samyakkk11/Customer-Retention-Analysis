import pandas as pd, numpy as np

# --- illustrative assumptions (label these in README/dashboard) ---
COST_PER_CONTACT = 5.0     # USD
MARGIN = 0.30              # contribution margin on an order

df = pd.read_csv("rfm_output.csv")
df = df.merge(pd.read_csv("rfm_powerbi.csv")[["Customer_ID", "HV_AtRisk"]], on="Customer_ID")
df["buyer"] = df["Completed_Orders"] > 0

# 1. Cancellation leak (assumes cancelled baskets ~ completed baskets)
print("Total_Orders - Completed - Cancelled:\n",
      (df["Total_Orders"] - df["Completed_Orders"] - df["Cancelled_Orders"]).describe().round(2))
aov = df["Total_Spending_USD"].sum() / df["Completed_Orders"].sum()
canc = df["Cancelled_Orders"].sum()
print(f"\nAOV ${aov:.1f} | cancelled orders {canc} | implied cancelled value ${canc*aov:,.0f} "
      f"vs realised ${df['Total_Spending_USD'].sum():,.0f}")

# 2. Do cancellations relate to churn / recency?
o = df[df["Total_Orders"] > 0].copy()
o["cancel_rate"] = o["Cancelled_Orders"] / o["Total_Orders"]
print("\nSpearman vs cancel_rate:\n", o[["cancel_rate", "Recency_Days", "Churn_Risk_Score",
      "Customer_Satisfaction_Score", "Total_Spending_USD"]].corr(method="spearman")["cancel_rate"].round(3))
o["band"] = pd.cut(o["cancel_rate"], [-0.01, 0, 0.34, 0.67, 1.0],
                   labels=["0%", "1-34%", "35-67%", "68-100%"])
print(o.groupby("band", observed=True).agg(users=("Customer_ID", "count"),
      recency=("Recency_Days", "mean"), churn=("Churn_Risk_Score", "mean"),
      inactive=("Is_Active_Customer", lambda s: 1 - s.mean())).round(2))

# 3. Non-buyer tiers
nb = df[~df["buyer"]].copy()
nb["tier"] = np.select([nb["Cancelled_Orders"] > 0, nb["Products_Added_To_Cart"] >= 10,
                        nb["Products_Added_To_Cart"] > 0],
                       ["Tried & cancelled", "Heavy cart, no order", "Light cart"],
                       default="No cart activity")
print("\n", nb["tier"].value_counts())
print(nb.groupby("tier")[["Total_Sessions", "Products_Added_To_Cart", "Recency_Days",
                          "Churn_Risk_Score"]].mean().round(1))

# 4. Campaign break-even
b = df[df["buyer"]]
targets = {"All At-Risk": b[b["RFM_Segment"] == "At-Risk"],
           "HV At-Risk": b[b["HV_AtRisk"]],
           "Critical churn": b[b["Churn_Risk_Level"] == "Critical"]}
rows = []
for name, t in targets.items():
    t_aov = t["Total_Spending_USD"].sum() / t["Completed_Orders"].sum()
    rows.append((name, len(t), round(t_aov, 1), round(len(t) * COST_PER_CONTACT),
                 round(COST_PER_CONTACT / (t_aov * MARGIN) * 100, 1)))
print("\n", pd.DataFrame(rows, columns=["target", "n", "aov", "campaign_cost", "breakeven_reactivation_%"]))