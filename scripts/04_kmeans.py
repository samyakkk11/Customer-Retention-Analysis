import pandas as pd
import numpy as np
import os; os.environ["LOKY_MAX_CPU_COUNT"] = "4"
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


df = pd.read_csv("rfm_output.csv")
b = df[df["RFM_Segment"] != "Never Purchased"].copy()

# Log-transform the skewed variables, then scale
X = np.log1p(b[["Recency_Days", "Completed_Orders", "Total_Spending_USD"]])
X = StandardScaler().fit_transform(X)

# Pick k using silhouette on a sample (full data is slow)
sample = X[np.random.RandomState(42).choice(len(X), 8000, replace=False)]
for k in range(3, 8):
    labels = KMeans(k, n_init=10, random_state=42).fit_predict(sample)
    print(k, round(silhouette_score(sample, labels), 3))

# Fit final model (set K after looking at the scores above)
K = 4
b["Cluster"] = KMeans(K, n_init=10, random_state=42).fit_predict(X)

print(b.groupby("Cluster").agg(
    n=("Customer_ID", "count"),
    recency=("Recency_Days", "mean"),
    orders=("Completed_Orders", "mean"),
    spend=("Total_Spending_USD", "mean")).round(1))
print(pd.crosstab(b["RFM_Segment"], b["Cluster"], normalize="index").round(2))

hv_risk = b[(b["RFM_Segment"] == "At-Risk") & (b["Cluster"] == 1)]
print(len(hv_risk), hv_risk["Total_Spending_USD"].sum().round(0),
      f'{hv_risk["Total_Spending_USD"].sum() / b["Total_Spending_USD"].sum():.1%}')
slim = pd.read_csv("rfm_powerbi.csv")
flag_ids = set(hv_risk["Customer_ID"])
slim["HV_AtRisk"] = slim["Customer_ID"].isin(flag_ids)
slim["Value_Cluster"] = slim["Customer_ID"].map(b.set_index("Customer_ID")["Cluster"])
slim.to_csv("rfm_powerbi.csv", index=False)