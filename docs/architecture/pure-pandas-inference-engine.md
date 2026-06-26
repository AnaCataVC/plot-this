# Pure Pandas Inference Engine: Internal Calculations

This document details exactly how our custom semantic inference engine (`analyzer.py`) calculates metadata, statistics, and bivariate insights using purely native Pandas operations. By abandoning heavy profilers, we built a bespoke, millisecond-fast engine.

## 1. Speed Optimization
For massive datasets, we impose a hard cap of `MAX_ROWS = 10000` via `df.sample(n=10000, random_state=42)`. This ensures that all downstream statistical calculations return instantly without freezing the Streamlit UI, while still providing a statistically significant sample.

## 2. Semantic Type Inference
Instead of relying on Pandas' physical memory types (`dtype`), we analyze the actual contents to deduce the *semantic* type:
1.  **Quantitative:** Analyzed using `pd.api.types.is_numeric_dtype(series)`. If the column is numeric but has **10 or fewer unique values**, it is coerced into a **Nominal** (Categorical) type to prevent irrelevant histograms and allow for grouping.
2.  **Temporal:** Detected using `pd.api.types.is_datetime64_any_dtype(series)`.
3.  **Nominal (Categorical):** Everything else, including text strings or coerced low-cardinality integers.

## 3. Univariate Statistics and Insights

For each column, we extract base metadata like the count of missing values (`series.isna().sum()`) and distinct values (`series.nunique()`).

### Quantitative Columns
We extract the following metrics dropping nulls (`series.dropna()`):
*   **Central Tendency & Spread:** `mean`, `median`, `std`, `min`, `max`.
*   **Distribution Shape (Skewness):** Calculated via `series.skew()`.
    *   If $|Skewness| < 0.5$: The distribution is considered symmetric.
    *   If $Skewness \ge 0.5$: Positive right skewness (concentration in lower values).
    *   If $Skewness \le -0.5$: Negative left skewness (concentration in higher values).
*   **Outliers:** We calculate the Interquartile Range ($IQR = Q3 - Q1$) and define the outlier bounds as $[Q1 - 1.5 \times IQR, \ Q3 + 1.5 \times IQR]$.

### Nominal Columns
We calculate frequency using `series.value_counts()`:
*   **Dominant Value:** The top index (`counts.index[0]`) and its relative frequency percentage.
*   **Cardinality Warning:** If a column has more than 15 unique categories, we trigger an insight warning about "high cardinality", suggesting grouping smaller categories when plotting.

## 4. Bivariate Insights

To provide advanced analytical value, we compute relationships between pairs of variables. To prevent UI freezing on wide datasets, we cap the categorical and numeric variables to a maximum of 15 each (yielding a maximum of 225 combinations).

### A. Numeric-Numeric Correlations
We calculate the Pearson correlation matrix using `df.corr(method="pearson", numeric_only=True)`.
For every pair of quantitative columns:
*   If the absolute correlation coefficient $|r| \ge 0.35$, we consider it a significant relationship.
*   We use `numpy.polyfit(x, y, 1)` to calculate the **slope** and **intercept** of the linear regression.
*   We generate an explicit insight indicating whether the relationship is "moderate" or "very strong" ($|r| \ge 0.7$), and exactly how much one variable increases/decreases for each unit of the other based on the calculated slope.

### B. Categorical-Numeric Interactions
We iterate through combinations of Nominal and Quantitative columns.
*   We group the data: `df.groupby(nominal_col)[quant_col].agg(["mean", "count"])`.
*   We filter out groups with fewer than 3 observations to ensure statistical relevance.
*   We identify the categories with the maximum and minimum mean values.
*   If the relative percentage difference between the highest and lowest mean is $\ge 15.0\%$, we generate an insight highlighting this significant variance between groups.
