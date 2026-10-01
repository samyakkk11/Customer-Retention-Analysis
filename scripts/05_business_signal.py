import pandas as pd, numpy as np
from scipy import stats

df = pd.read_csv("rfm_output.csv")
df["buyer"] = df["Completed_Orders"] > 0

# C: conversion and revenue per user by dimension
for c in ["Preferred_Marketing_Channel", "Preferred_Device", "Preferred_Category",
          "Preferred_Payment_Method", "Continent"]:
    t = df.groupby(c).agg(users=("Customer_ID", "count"),
                          conv=("buyer", "mean"),
                          rev=("Total_Spending_USD", "sum"))
    t["rev_per_user"] = t["rev"] / t["users"]
    chi2, p, *_ = stats.chi2_contingency(pd.crosstab(df[c], df["buyer"]))
    print(f"\n{c}  (chi-square p={p:.3g})")
    print(t.round(3))

# C: cancellation
print("\nCancel rate overall:",
      (df["Cancelled_Orders"].sum() / df["Total_Orders"].sum()).round(3))
t = df.groupby("Preferred_Category")[["Cancelled_Orders", "Total_Orders"]].sum()
print((t["Cancelled_Orders"] / t["Total_Orders"]).round(3))

# B: buyers vs non-buyers
cols = ["Total_Sessions", "Products_Viewed", "Products_Added_To_Cart",
        "Wishlist_Items", "Cancelled_Orders", "Customer_Age"]
print("\n", df.groupby("buyer")[cols].mean().round(1))

nb = df[~df["buyer"]]
print("\nNon-buyers:", len(nb))
print("With cart adds:", (nb["Products_Added_To_Cart"] > 0).sum())
print("With a cancelled order:", (nb["Cancelled_Orders"] > 0).sum())
print("Cart adds >= 10:", (nb["Products_Added_To_Cart"] >= 10).sum())