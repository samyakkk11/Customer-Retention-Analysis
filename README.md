# Customer Retention Analysis: Who to Win Back, Where Sales Leak, and What to Test First

**Python (pandas, SciPy, scikit-learn) + Power BI (DAX, What-If parameters)**

## Business summary

An online store has 100,000 registered customers, but only 30.6% have ever bought anything, and 44.6% of all orders are cancelled. This project segments the 30,622 buyers by recency, frequency and spend (RFM), finds where sales are leaking, and sizes a win-back campaign with adjustable assumptions. The main finding: about 1,800 high-spending customers have gone quiet and hold 17.3% of all buyer revenue, so they are the best group to test a win-back offer on first.

> **Data note:** the dataset is synthetic (Kaggle). Several columns behave like random noise (for example complaints and discount usage do not differ by segment), and every customer who ordered has at least one cancellation. The findings show the method and the kind of decisions it supports, not real market facts.

## Business questions

1. **Who is worth keeping, and where should a limited retention budget go first?**
2. **Where does the store lose sales: who never buys, and why do orders fail?**
3. **Does a win-back campaign pay off, and how do we find out for real?**

## Dashboard

| Page | Question | Headline |
|---|---|---|
| 1. The big picture | Who are our customers? | Only 3 in 10 sign-ups buy; 1,772 big spenders have gone quiet |
| 2. Where we lose sales | Where is the leak? | 20,128 people tried to buy and every order was cancelled |
| 3. What to do first | Does a campaign pay off? | Start small, test it, scale only past the break-even |

<!-- Add screenshots to /images and keep these filenames, or edit the paths -->
![Page 1 - The big picture](images/page1_big_picture.png)
![Page 2 - Where we lose sales](images/page2_where_we_lose_sales.png)
![Page 3 - What to do first](images/page3_what_to_do_first.png)

The Power BI file is in [`dashboard/retention_dashboard.pbix`](dashboard/retention_dashboard.pbix). Page 3 has sliders for cost per contact, margin and win-back rate, so a reader can test their own assumptions.

## Key findings

**1. Most sign-ups never buy.** 30,622 of 100,000 customers (30.6%) have a completed order. About 18,300 bought more than once (18.3% of sign-ups, 60% of buyers).

**2. A few groups carry most of the sales.** RFM scoring (quintiles, buyers only) gives six segments:

| Segment | Customers | % of buyers | % of revenue | Avg days since purchase | Avg orders | Avg spend |
|---|---|---|---|---|---|---|
| At-Risk | 7,367 | 24.1% | 34.0% | 51 | 3.6 | $515 |
| Champions | 3,979 | 13.0% | 27.3% | 6 | 4.9 | $764 |
| Loyal | 7,027 | 22.9% | 24.8% | 12 | 3.0 | $392 |
| Promising | 4,918 | 16.1% | 5.6% | 6 | 1.0 | $126 |
| Lost | 4,882 | 15.9% | 5.6% | 50 | 1.0 | $127 |
| Needs Attention | 2,449 | 8.0% | 2.8% | 16 | 1.0 | $126 |

Total buyer revenue is $11.1M. The At-Risk segment is the biggest by revenue, ahead of Champions.

**3. Half of the At-Risk revenue sits with about 1,800 customers.** K-means (K=4) on log-scaled R/F/M put 1,772 At-Risk customers in the highest-value cluster. They hold **$1.92M of historical spend, 17.3% of all buyer revenue** (about half of the At-Risk segment's revenue), and average about $1,086 each.

**4. Orders fail everywhere.** 63,863 of 143,114 orders (44.6%) are cancelled, and the rate is almost identical across all 15 product categories (43.8% to 45.6%). That points to a process problem (checkout, payment or delivery), not a product problem. 20,128 customers placed orders and never completed one.

**5. Channel, device, category, payment method and region do not change who buys.** Conversion is 30 to 31% in every group and no chi-square test is significant at 5% (marketing channel is the closest, p = 0.077, with Organic Search at 32.0%). Moving budget between these would not help on this data.

**6. The non-buyers are not equally cold.** Of 69,378 non-buyers: 28,338 added a few items to a cart, 20,128 tried and had every order cancelled, 12,791 never touched a cart, and 8,121 added 10 or more items without ordering.

**7. A win-back pilot on the 1,772 quiet big spenders is a cheap bet.** At illustrative assumptions ($5 per contact, 30% margin) it costs $8,860 and breaks even if 10.1% of them place one order. Contacting the whole At-Risk segment (7,367 people) breaks even at 11.7%.

## Method

1. **Inspect and clean (`01_eda.py`).** 100,000 rows, 50 columns, no nulls, no duplicate IDs. Found that 69% of customers have zero spend, so the built-in `RFM_Score` (almost all 7s) is not usable. `Loyalty_Tier` is "Bronze" for every row and was dropped.
2. **RFM on buyers only (`02_rfm.py`).** Recency = `Recency_Days`, Frequency = `Completed_Orders`, Monetary = `Total_Spending_USD`. Quintile scores 1 to 5, rule-based segments, plus a "Never Purchased" group for the 69,378 non-buyers.
3. **Statistical checks (`03_stats.py`).** Tests use variables that were *not* used to build the segments, because testing recency or spend across RFM segments would be circular.
   - Chi-square, segment vs churn risk level: p < 0.001, Cramér's V = 0.15 (weak to modest). Critical risk is concentrated in At-Risk (9.3%) and Lost (9.6%) and near 0% elsewhere.
   - Kruskal-Wallis (used because spend and counts are heavily skewed): satisfaction is statistically significant but the means differ by only 0.1 points (3.71 to 3.81), which is not a practical difference. Complaints (p = 0.63) and discount usage (p = 0.17) do not differ by segment.
   - Cart abandonment looked higher for Champions in raw counts, but the abandonment rate is flat (0.30 to 0.33) across segments. The raw difference came from Champions having more carts.
   - 95% confidence intervals for mean spend per segment (descriptive only).
4. **K-means check (`04_kmeans.py`).** The clusters broadly reproduce the value tiers of the rules (Lost and Needs Attention fall 100% in the low-value cluster) but weight spend and frequency more than recency, which surfaced the 1,772 quiet high spenders.
5. **Business signal and decisions (`05_business_signal.py`, `06_decisions.py`).** Conversion by channel, device, category, payment method and continent; cancellation analysis; non-buyer tiers; campaign break-even.
6. **Dashboard prep (`07_rfm_output.py`).** Exports a slim, 20-column file for Power BI with segment, cluster, non-buyer tier and campaign target flags.
7. **Power BI.** Three pages, DAX measures, and What-If parameters for cost per contact, margin and win-back rate.

## Recommendations

1. **Do not move marketing budget by channel, device, category or region.** None of them separates buyers from non-buyers.
2. **Find out why orders are cancelled before spending more on ads.** 20,128 customers never completed an order. For scale: the implied value of all cancelled orders is about $9.0M at the average order value of $140.50, and if 1 in 10 of the all-cancelled customers completed one order it would be about $283K (illustrative sizing, assumes cancelled baskets are worth about the same as completed ones).
3. **Run a win-back pilot on the 1,772 quiet big spenders, with a holdout group.**
   - Send the offer to a random 90% and nothing to the other 10%.
   - Wait 30 days, then compare repeat purchases in both groups.
   - The difference is the real win-back rate. Scale up only if it clears the break-even (about 10% at the assumptions above).

The actual win-back rate cannot be known from this data, which is why the recommendation is a test and not a forecast.

## Repository structure

```
customer-retention-rfm/
├── scripts/
│   ├── 01_eda.py
│   ├── 02_rfm.py
│   ├── 03_stats.py
│   ├── 04_kmeans.py
│   ├── 05_business_signal.py
│   ├── 06_decisions.py
│   └── 07_rfm_output.py
├── dashboard/
│   └── retention_dashboard.pbix
├── images/
│   ├── page1_big_picture.png
│   ├── page2_where_we_lose_sales.png
│   └── page3_what_to_do_first.png
├── data/  (campaign_targets.csv, rfm_powerbi.csv)
└── README.md
```

## How to run

1. Download the dataset from Kaggle (link below) and save the CSV as `ecommerce_customer_behavior_2026.csv` in the folder you run the scripts from.
2. Install the libraries: `pip install pandas numpy scipy scikit-learn`
3. Run the scripts in order (`01_eda.py` through `07_rfm_output.py`). Each one reads the CSV written by the earlier ones (`rfm_output.csv`, `rfm_powerbi.csv`).
4. Open `dashboard/retention_dashboard.pbix` in Power BI Desktop.

## Limitations

- **Synthetic data.** Real customer data is rarely this uniform. Some columns behave like noise, and every customer who ordered has at least one cancelled order, which is probably an artifact of how the data was generated.
- **Ties in frequency.** Many customers have the same number of orders, so scores were assigned with `rank(method="first")`. Customers with equal order counts can land in different F scores, though this does not change any segment label.
- **Rule-based segments.** The cut-offs are a judgement call. K-means is a cross-check, not a replacement: silhouette scores are low (about 0.33 to 0.38 across K = 3 to 7), so the data is a continuum and not clearly separated groups. K = 4 was chosen for interpretability.
- **Churn risk is partly derived from recency** (correlation 0.39), so its agreement with the segments is only partly independent.
- **Revenue figures are historical spend,** not a forecast of what would be lost.
- **Campaign figures are illustrative.** Cost per contact, margin and win-back rate are assumptions, and the model assumes one order per customer won back.
- **No customer-level churn model.** `Is_Active_Customer` is almost entirely a recency cutoff, so predicting it would be circular, and the project deliberately avoids it.

## Dataset

[E-Commerce Customer Behavior Dataset 2026](https://www.kaggle.com/datasets/datascikhan/e-commerce-customer-behavior-dataset-2026) on Kaggle (100,000 customers, 50 columns). The raw file is not included in this repository.

## Author

**Samyak Prabhulkar**, aspiring data analyst, Mumbai.
[LinkedIn](www.linkedin.com/in/samyak-prabhulkar-353363210) | [GitHub](https://github.com/samyakkk11/Customer-Retention-Analysis.git)
