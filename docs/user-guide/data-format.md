# Supported Data Format in PlotThis

To ensure that the semantic inference engine and the chart generator work with maximum precision, we recommend preparing your CSV or Excel files following these guidelines:

---

## 1. Headers in the First Row
*   The first row of your file must contain the descriptive names of each column (e.g., `Date`, `Product`, `Sales`, `Marketing_Budget`).
*   Avoid leaving the first row empty or using duplicate names, as this could cause errors in Pandas' initial parsing.

## 2. Date Format (Temporal Variables)
The typing engine looks for and analyzes common date patterns. To ensure correct inference as a **`Temporal`** variable, use standard formats such as:
*   `YYYY-MM-DD` (e.g., `2026-01-25`)
*   `YYYY-MM-DD HH:MM:SS` (e.g., `2026-01-25 14:30:00`)
*   `DD/MM/YYYY` (e.g., `25/01/2026`)

*Note:* If a column contains dates with mixed or inconsistent formats, it might be classified as a Categorical (Nominal) variable.

## 3. Number Cleaning (Quantitative Variables)
Numeric columns must contain exclusively digits and decimal points to be classified as **`Quantitative`**:
*   **Currency Symbols:** Avoid including currency symbols (such as `$`, `€`) or letters inside the cells in your raw data file (e.g., use `4500` instead of `$4,500` or `4500 USD`).
*   **Thousands Separators:** It is recommended not to use thousands separators with commas unless strictly necessary, as it can confuse the parser (e.g., use `15000` instead of `15,000`). The decimal separator must be the period `.`.
*   *Cardinality Coercion:* If a numeric column contains few unique values (less than 10 discrete categories, like codes `[0, 1, 2]`), the engine will treat it as **`Nominal`** to facilitate grouped bar charts and logical comparisons.

## 4. Categorical Variables (Nominal)
*   They represent text, categories, or labels (e.g., `Technology`, `Home`, `Clothing`).
*   If a categorical column has **high cardinality** (more than 15 unique categories), the tool will warn you in the univariate insights and suggest horizontal charts sorted with scroll bars to prevent labels from overlapping on the screen.

## 5. Missing Values (Nulls)
*   You do not need to delete rows with missing values. The tool automatically handles blanks (`NaN`, `None`, empty cells) by omitting them in mathematical calculations so they do not distort averages or correlations.
*   The univariate insights card will explicitly report the count and percentage of missing values found per column.
