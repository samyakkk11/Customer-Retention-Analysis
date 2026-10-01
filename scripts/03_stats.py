import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv("rfm_output.csv")
b = df[df["RFM_Segment"] != "Never Purchased"].copy()

# --- Test 1: Chi-square, segment vs churn risk level ---
ct = pd.crosstab(b["RFM_Segment"], b["Churn_Risk_Level"])
chi2, p, dof, _ = stats.chi2_contingency(ct)
n = ct.values.sum()
cramers_v = np.sqrt(chi2 / (n * (min(ct.shape) - 1)))
print(f"Chi-square p={p:.2e}, Cramer's V={cramers_v:.3f}")
print((ct.div(ct.sum(axis=1), axis=0) * 100).round(1))

# --- Test 2: Kruskal-Wallis on variables NOT used in scoring ---
for col in ["Customer_Satisfaction_Score", "Cart_Abandonment_Count",
            "Complaint_Count", "Discount_Usage_Count"]:
    groups = [g[col].values for _, g in b.groupby("RFM_Segment")]
    h, p = stats.kruskal(*groups)
    print(f"\n{col}: H={h:.1f}, p={p:.3g}")
    print(b.groupby("RFM_Segment")[col].agg(["mean", "median"]).round(2))

# --- Test 3: 95% CI for mean spend per segment ---
rows = []
for seg, g in b.groupby("RFM_Segment"):
    x = g["Total_Spending_USD"]
    lo, hi = stats.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=stats.sem(x))
    rows.append((seg, len(x), round(x.mean(), 1), round(lo, 1), round(hi, 1)))
print(pd.DataFrame(rows, columns=["segment", "n", "mean_spend", "ci_low", "ci_high"]))

b["Abandon_Rate"] = b["Cart_Abandonment_Count"] / b["Products_Added_To_Cart"].replace(0, np.nan)
print(b.groupby("RFM_Segment")["Abandon_Rate"].agg(["mean", "median"]).round(3))