import pandas as pd, numpy as np

df = pd.read_csv("rfm_output.csv")
slim = pd.read_csv("rfm_powerbi.csv")

tier = np.select(
    [df["Completed_Orders"] > 0, df["Cancelled_Orders"] > 0,
     df["Products_Added_To_Cart"] >= 10, df["Products_Added_To_Cart"] > 0],
    ["Buyer", "Tried & cancelled", "Heavy cart, no order", "Light cart"],
    default="No cart activity")
extra = df[["Customer_ID", "Total_Orders", "Cancelled_Orders", "Total_Sessions",
            "Products_Added_To_Cart", "Preferred_Marketing_Channel",
            "Preferred_Device"]].copy()
extra["Non_Buyer_Tier"] = tier
slim = slim.drop(columns=[c for c in extra.columns if c != "Customer_ID" and c in slim.columns])
slim = slim.merge(extra, on="Customer_ID", how="left")
slim.to_csv("rfm_powerbi.csv", index=False)
print(slim["Non_Buyer_Tier"].value_counts())

# campaign target table
b = df[df["Completed_Orders"] > 0].merge(slim[["Customer_ID", "HV_AtRisk"]], on="Customer_ID")
targets = {"All At-Risk": b[b["RFM_Segment"] == "At-Risk"],
           "HV At-Risk": b[b["HV_AtRisk"]],
           "Critical churn": b[b["Churn_Risk_Level"] == "Critical"]}
rows = [(k, len(t), t["Total_Spending_USD"].sum() / t["Completed_Orders"].sum())
        for k, t in targets.items()]
pd.DataFrame(rows, columns=["target", "customers", "aov"]).to_csv("campaign_targets.csv", index=False)
print(pd.read_csv("campaign_targets.csv"))