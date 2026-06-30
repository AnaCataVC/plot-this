# Pure Pandas Inference Engine: Internal Calculations

This document details exactly how our custom semantic inference engine (`analyzer.py`) calculates metadata, statistics, and bivariate insights using purely native Pandas operations. By abandoning heavy profilers, we built a bespoke, millisecond-fast engine.

## 1. Speed Optimization
For massive datasets, we impose a hard cap of `MAX_ROWS = 10000` via `df.sample(n=10000, random_state=42)`. This ensures that all downstream statistical calculations return instantly without freezing the Streamlit UI, while still providing a statistically significant sample.

## 2. Semantic Type Inference
Instead of relying on Pandas' physical memory types (`dtype`), we analyze the actual contents to deduce the *semantic* type:
1.  **Continuous Quantitative:** Analyzed using `pd.api.types.is_numeric_dtype(series)`. If the column is numeric and has more than 15 unique values.
2.  **Discrete Quantitative (Ordinal/Low-Cardinality):** If the column is numeric and has **15 or fewer unique values**, it is classified as Discrete Quantitative. This preserves mathematical ordinality on axes and sequential palettes instead of treating them as unordered categories.
3.  **Temporal:** Detected using `pd.api.types.is_datetime64_any_dtype(series)`.
4.  **Nominal (Categorical):** String columns, boolean columns, or mixed columns.

## 3. Univariate Statistics and Insights

For each column, we extract base metadata like the count of missing values (`series.isna().sum()`) and distinct values (`series.nunique()`).

### Quantitative Columns (Continuous and Discrete)
We extract the following metrics dropping nulls (`series.dropna()`):
*   **Central Tendency & Spread:** `mean`, `median`, `std`, `min`, `max`.
*   **Distribution Shape (Skewness):** Calculated via `series.skew()`.
    *   If $|Skewness| < 0.5$: The distribution is considered symmetric.
    *   If $Skewness \ge 0.5$: Positive right skewness (concentration in lower values).
    *   If $Skewness \le -0.5$: Negative left skewness (concentration in higher values).
*   **Outliers:** We calculate the Interquartile Range ($IQR = Q3 - Q1$) and define the outlier bounds as $[Q1 - 1.5 \times IQR, \ Q3 + 1.5 \times IQR]$. For highly skewed variables, outliers are flagged with caution tags.

### Nominal Columns
We calculate frequency using `series.value_counts()`:
*   **Dominant Value:** The top index (`counts.index[0]`) and its relative frequency percentage.
*   **Cardinality Warning:** If a column has more than 15 unique categories, we trigger an insight warning about "high cardinality", recommending horizontal bar charts.

## 4. Bivariate Insights

To provide advanced analytical value, we compute relationships between pairs of variables. To prevent UI freezing on wide datasets, we cap the categorical and numeric variables to a maximum of 15 each (yielding a maximum of 225 combinations).

### A. Numeric-Numeric Correlations (Anscombe Proofing)
We calculate the correlation matrix using both Pearson (linear) and Spearman (monotonic non-linear) methods via `df.corr(method=..., numeric_only=True)`.
For every pair of quantitative columns:
*   We use the maximum absolute correlation coefficient $max(|r_{\text{Pearson}}|, |r_{\text{Spearman}}|)$.
*   If this maximum $|r| \ge 0.35$, we consider it a significant relationship.
*   We use `numpy.polyfit(x, y, 1)` to calculate the **slope** and **intercept** of the linear regression.
*   We generate an explicit insight indicating whether the relationship is "moderate" or "very strong" ($|r| \ge 0.7$). If Spearman is significantly stronger than Pearson, we note the relationship is non-linear.

### B. Categorical-Numeric Interactions (Cohen's d Variant)
We iterate through Nominal and Quantitative column combinations.
*   We group the data: `df.groupby(nominal_col)[quant_col].agg(["mean", "count"])`.
*   We filter out groups with fewer than 5 observations (`count >= 5`) to filter statistical noise.
*   We calculate the global standard deviation ($\sigma_{\text{global}}$) of the numeric column.
*   We calculate the effect size:
    $$\text{Effect Size} = \frac{|\mu_{\text{max}} - \mu_{\text{min}}|}{\sigma_{\text{global}}}$$
*   If $\text{Effect Size} \ge 0.5$, we generate an insight highlighting this significant variance between groups, avoiding division by zero errors when the minimum is zero or negative.
