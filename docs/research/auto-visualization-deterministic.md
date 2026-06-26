> **Created:** 2026-06-24
> **Last Updated:** 2026-06-24

# Research: Deterministic Data Visualization Recommendation

This document compiles research on deterministic tools and methodologies (not based on AI/LLMs) that analyze datasets and automatically propose the best charts.

---

## 1. Technical Analysis of Existing Python Tools (Extra Step)

Below is a detailed breakdown of the internal logic, type inference mechanism, and algorithms used by leading open-source libraries to propose charts without using Artificial Intelligence:

### A. ydata-profiling (formerly pandas-profiling)
*   **Type Inference Mechanism:** Uses the **`visions`** library as its core engine. This library goes beyond the physical storage type limit of Pandas (`dtype` like `object` or `int64`) and models a graph of semantic types (e.g., identifying if a text series contains sequential numbers or dates and performing an implicit semantic conversion).
*   **Selection Algorithm:** Generates comprehensive HTML reports based on the nature of the detected type:
    *   *Univariate:* If the column is numeric (Quantitative), it draws distribution histograms and analyzes quartiles and extreme values. If it's categorical, it calculates absolute frequencies and cardinality.
    *   *Cross-correlations:* Automatically calculates Pearson, Spearman, Kendall, Cramer's V (for nominal variables) and **$\phi_K$ (Phik)**, a robust coefficient for capturing non-linear associations between mixtures of numeric and categorical variables. The highest scoring correlations generate automatic bivariate charts.
*   **Standard usage code:**
    ```python
    from ydata_profiling import ProfileReport
    profile = ProfileReport(df, infer_dtypes=True)
    profile.to_file("report.html")
    ```

### B. Sweetviz
*   **Type Inference Mechanism:** Autonomously classifies variables into three categories: Numeric, Categorical, and Text, based on the proportion of numeric values and the cardinality of the records.
*   **Selection Algorithm:** Its strength lies in **Target Analysis**. If the user defines a control column (target), Sweetviz automatically calculates univariate and bivariate associations by crossing each variable in the dataset against the target variable. If the target variable is binary, it generates grouped box plots; if continuous, it calculates locally smoothed correlation curves (LOESS) and overlapping distributions.
*   **Standard usage code:**
    ```python
    import sweetviz as sv
    report = sv.analyze(df, target_feat="target_variable")
    report.show_html()
    ```

### C. AutoViz (by Abid Ali Awan)
*   **Type Inference Mechanism:** Quickly classifies columns by analyzing the count of unique values. For instance, if a numeric column contains fewer than 20 unique values, it automatically reclassifies it as categorical (Nominal/Ordinal) to avoid incoherent continuous charts.
*   **Selection Algorithm:** Uses a series of performance heuristics to avoid overwhelming the user:
    *   If there are more than 10 numeric variables, it calculates correlation and generates Scatter Plots only for the pairs that exceed a certain correlation threshold, limiting the total number of charts to display.
    *   Automatically selects between bar charts, histograms, Box Plots, and violin plots (to contrast numeric distributions by categories) based on the total number of records and columns.
*   **Standard usage code:**
    ```python
    from autoviz.AutoViz_Class import AutoViz_Class
    AV = AutoViz_Class()
    dft = AV.AutoViz(filename="file.csv", sep=",", depVar="target_variable")
    ```

### D. D-Tale
*   **Type Inference Mechanism:** Uses a Flask backend coupled with a React frontend. It directly maps the physical data types of the DataFrame to a metadata dictionary in JS.
*   **Selection Algorithm:** Unlike static generators, D-Tale exposes a dynamic interactive chart builder that **enables/disables options based on the selection**:
    *   If the user selects a single quantitative column, it blocks complex options and suggests a Histogram or Box Plot.
    *   If they select 1 nominal and 1 quantitative variable, it enables bar charts by aggregating the metric (average, sum, median) or segmented histograms.
*   **Standard usage code:**
    ```python
    import dtale
    d = dtale.show(df)
    d.open_browser()
    ```

### E. Lux (The most advanced recommendation experience)
*   **Type Inference Mechanism:** Analyzes the DataFrame and infers semantic types based on the range of values and common column names (e.g., dates).
*   **Selection Algorithm (Interestingness Scoring):** It's the most advanced statistical rules engine without AI. Its engine evaluates the interestingness of charts based on the following ranking heuristics:
    *   *For line and bar charts (without filters):* Calculates **Unevenness/Skewness** by measuring the Euclidean distance (L2 norm) between the observed distribution and a uniform (flat) distribution. The more irregular the distribution, the higher the interestingness score.
    *   *For charts with applied filters:* Measures **Deviation from Overall** by comparing the subset's distribution against the overall dataset's using scaled L2 distances.
    *   *For Scatter Plots:* Measures **Monotonicity** to prioritize and suggest pairs of numeric variables that show a constant and linear trend.
*   **Standard usage code:**
    ```python
    import lux
    import pandas as pd
    df = pd.read_csv("data.csv")
    df  # The output in Jupyter shows an interactive tab with the suggestions above
    ```

---

## 2. Existing Deterministic Web Tools

These cloud applications analyze the data structure to determine visualizations without relying on natural language processing or AI:

### A. LiveGap Charts
*   **What it does:** Proactively enables compatible chart templates in its dashboard when pasting a flat dataset.
*   **Logic:** Analyzes if the pasted format corresponds to a one-dimensional, two-dimensional, or time-series table, blocking incompatible visual options (e.g., disables scatter plots if it doesn't detect at least two numeric series).
*   **Link:** [LiveGap Charts](https://charts.livegap.com/)

### B. Chartle.es
*   **What it does:** Generates the chart immediately based on an interactive wizard and allows switching between rendering formats.
*   **Logic:** Structured validation of input fields using hard constraints per chart (e.g., radar charts require multiple dimensions but only one metric).

---

## 3. Recommendation Logic in Classic Corporate Tools

Classic Business Intelligence suites and spreadsheets use deterministic decision engines based on traditional visualization rules:

*   **Excel and Google Sheets ("Recommended Charts"):** The software evaluates the orientation of the dataset (horizontal/vertical) and the presence of headers. If it detects a date type column on the left and continuous values on the right, it prioritizes the line chart. If the left column contains low-cardinality text, it suggests a bar chart.
*   **Tableau Public ("Show Me"):** Implements the industry's most rigid and robust visualization rules engine. Each chart type has minimum and maximum dimension and measure requirements:
    *   *Symbol Map:* Requires 1 geographic field, 0 or more dimensions, and 0 to 2 measures.
    *   *Scatter Plot:* Requires exactly 0 or more dimensions and between 2 and 4 measures.
*   **Power BI:** Uses the inference of the local database schema and relationships declared in the star model to generate the initial default chart when dragging columns to the canvas.

---

## 4. 🧪 The Technological Gap / Opportunity (What does NOT exist without AI?)

By contrasting these tools, a clear development opportunity is identified:

> **There is no lightweight open-source tool executed entirely on the web (Client-Side) that takes a flat CSV file from the user and applies local statistical distribution and correlation tests to propose a ranked list of charts (including outlier analysis, explained box plots, treemaps, and optimal histograms) without compromising data privacy.**

Python tools (like Lux or Profiling) require programming knowledge and local Jupyter servers. Tools like Excel or Tableau are very heavy paid applications. And modern AI alternatives require uploading confidential information to the cloud.

---

## 5. Logic Flow Design and Heuristics for our Tool

We will implement this architecture modularly in JavaScript:

### Semantic Type Inference
Our algorithms will analyze the first 100 rows of each column in the CSV:
1.  **Temporal (T):** If at least 80% of the non-empty values pass the date parsing test (`!isNaN(Date.parse(val))` and match common patterns like `YYYY-MM-DD` or timestamps).
2.  **Quantitative (Q):** If at least 90% of the values can be converted to a number (`!isNaN(Number(val))`).
    *   *Subclassification:* If the quantitative column has a cardinality $< 10$, it is marked as ordinal categorical to enable fast aggregations.
3.  **Nominal (N):** Text strings that do not qualify as numeric or date.

### Recommendation Decision Matrix

| Data Type | Key Statistical Metric | Suggested Chart | Technical Logic and Criteria |
| :--- | :--- | :--- | :--- |
| **1 Q** | Kurtosis and Distribution Skewness | **Histogram** and **Box Plot** | Shows the distribution. If the skewness is very pronounced ($|Skewness| > 1$), a note is added explaining the sample's asymmetry. |
| **1 N** | Cardinality (Unique values) | **Bar Chart** | If cardinality is $\le 10$, standard vertical bars. If between 11 and 25, horizontal bars with scroll. If $> 25$, suggests grouping the excess in "Others". |
| **2 Q** | Pearson Coefficient ($r$) | **Scatter Plot** | If there is moderate/high linear correlation ($|r| \ge 0.35$). The least squares linear regression line ($y = mx + b$) is calculated and plotted. |
| **1 T + 1 Q** | Constant time interval | **Line Chart** | Represents the temporal evolution of the quantitative value. |
| **1 N + 1 Q** | Variance between groups | **Grouped Bars (Means)** | Groups the numeric variable calculating the average for each nominal category. |
| **2 N** | Cross-category count | **Contingency Heatmap** | Crossed matrix of relative frequencies. |
