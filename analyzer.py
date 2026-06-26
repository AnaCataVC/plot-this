import pandas as pd
import numpy as np
import sys
import os

def extract_metadata(df: pd.DataFrame, lang: str = "es") -> dict:
    """
    Analyzes the DataFrame directly using pure pandas to extract a clean structure
    of columns, types, and basic univariate insights in the specified language (es/en).
    """
    metadata = {}
    
    # We sample if the dataset is massive, just for speed, though Pandas is usually fast enough
    MAX_ROWS = 10000
    if len(df) > MAX_ROWS:
        df_sample = df.sample(n=MAX_ROWS, random_state=42)
    else:
        df_sample = df
        
    for col in df_sample.columns:
        series = df_sample[col]
        n_missing = int(series.isna().sum())
        p_missing = float(n_missing / len(df_sample)) if len(df_sample) > 0 else 0.0
        n_distinct = int(series.nunique(dropna=True))
        
        # Determine simplified type
        if pd.api.types.is_numeric_dtype(series):
            if n_distinct <= 10 and pd.api.types.is_integer_dtype(series):
                orig_type = "Categorical"
                simple_type = "Nominal"
            else:
                orig_type = "Numeric"
                simple_type = "Quantitative"
        elif pd.api.types.is_datetime64_any_dtype(series):
            orig_type = "DateTime"
            simple_type = "Temporal"
        else:
            orig_type = "Categorical"
            simple_type = "Nominal"
            
        col_meta = {
            "name": col,
            "original_type": orig_type,
            "type": simple_type,
            "n_distinct": n_distinct,
            "n_missing": n_missing,
            "p_missing": p_missing,
            "insights": []
        }
        
        # Missing values insight
        if n_missing > 0:
            if lang == "es":
                col_meta["insights"].append(
                    f"Contiene {n_missing} valores faltantes ({p_missing*100:.1f}% del total)."
                )
            else:
                col_meta["insights"].append(
                    f"Contains {n_missing} missing values ({p_missing*100:.1f}% of total)."
                )
                
        if simple_type == "Quantitative":
            s_clean = series.dropna()
            
            mean_val = float(s_clean.mean()) if not s_clean.empty else 0
            median_val = float(s_clean.median()) if not s_clean.empty else 0
            std_val = float(s_clean.std()) if len(s_clean) > 1 else 0
            skewness = float(s_clean.skew()) if len(s_clean) > 2 else 0
            min_val = float(s_clean.min()) if not s_clean.empty else 0
            max_val = float(s_clean.max()) if not s_clean.empty else 0
            
            q1 = float(s_clean.quantile(0.25)) if not s_clean.empty else 0
            q3 = float(s_clean.quantile(0.75)) if not s_clean.empty else 0
            iqr = q3 - q1
            
            col_meta["stats"] = {
                "mean": mean_val,
                "median": median_val,
                "std": std_val,
                "min": min_val,
                "max": max_val,
                "skewness": skewness,
                "iqr": iqr
            }
            
            # Skewness insights
            if pd.isna(skewness): skewness = 0
            if abs(skewness) < 0.5:
                if lang == "es": col_meta["insights"].append(f"La distribución es relativamente simétrica (sesgo: {skewness:.2f}).")
                else: col_meta["insights"].append(f"The distribution is relatively symmetric (skewness: {skewness:.2f}).")
            elif skewness >= 0.5:
                if lang == "es": col_meta["insights"].append(f"La distribución presenta asimetría positiva a la derecha (sesgo: {skewness:.2f}), sugiriendo una concentración en valores más bajos.")
                else: col_meta["insights"].append(f"The distribution shows positive right skewness (skewness: {skewness:.2f}), suggesting concentration in lower values.")
            else:
                if lang == "es": col_meta["insights"].append(f"La distribución presenta asimetría negativa a la izquierda (sesgo: {skewness:.2f}), sugiriendo concentración en valores altos.")
                else: col_meta["insights"].append(f"The distribution shows negative left skewness (skewness: {skewness:.2f}), suggesting concentration in higher values.")
                
            if iqr > 0:
                col_meta["stats"]["outlier_bounds"] = (q1 - 1.5 * iqr, q3 + 1.5 * iqr)
                
        elif simple_type == "Nominal":
            s_clean = series.dropna()
            if not s_clean.empty:
                counts = s_clean.value_counts()
                top_val = counts.index[0]
                freq_val = int(counts.iloc[0])
            else:
                top_val = "N/A"
                freq_val = 0
                
            col_meta["stats"] = {
                "top": str(top_val),
                "freq": freq_val,
            }
            
            if freq_val > 0 and len(df_sample) > 0:
                pct = (freq_val / len(df_sample)) * 100
                if lang == "es": col_meta["insights"].append(f"El valor dominante es **'{top_val}'**, representando el {pct:.1f}% de las filas ({freq_val} apariciones).")
                else: col_meta["insights"].append(f"The dominant value is **'{top_val}'**, representing {pct:.1f}% of rows ({freq_val} occurrences).")
                
            if n_distinct > 15:
                if lang == "es": col_meta["insights"].append(f"Alta cardinalidad ({n_distinct} categorías únicas). Se sugiere agrupar categorías menores al graficar.")
                else: col_meta["insights"].append(f"High cardinality ({n_distinct} unique categories). Suggest grouping smaller categories when plotting.")
                
        metadata[col] = col_meta
        
    return metadata

def calculate_bivariate_insights(df: pd.DataFrame, metadata: dict, lang: str = "es") -> list:
    """
    Analyzes bivariate relations (correlations and group variances)
    to draft explicit statistical insights in Spanish or English.
    """
    bivariate_insights = []
    
    # 1. Numeric-Numeric Correlation Analysis
    pearson_df = df.corr(method="pearson", numeric_only=True)
    
    if pearson_df is not None:
        numeric_cols = pearson_df.columns.tolist()
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                col1 = numeric_cols[i]
                col2 = numeric_cols[j]
                
                if col1 in metadata and col2 in metadata:
                    if metadata[col1]["type"] == "Quantitative" and metadata[col2]["type"] == "Quantitative":
                        coef = pearson_df.loc[col1, col2]
                        if not pd.isna(coef) and abs(coef) >= 0.35:
                            sub_df = df[[col1, col2]].dropna()
                            if len(sub_df) > 5:
                                x = sub_df[col1].values
                                y = sub_df[col2].values
                                slope, intercept = np.polyfit(x, y, 1)
                                
                                if lang == "es":
                                    rel_type = "positiva" if coef > 0 else "negativa"
                                    force = "muy fuerte" if abs(coef) >= 0.7 else "moderada"
                                    insight_text = (
                                        f"**Relación entre '{col1}' y '{col2}':** "
                                        f"Existe una correlación lineal {rel_type} {force} ($r = {coef:.2f}$). "
                                        f"En promedio, por cada unidad que aumenta *'{col1}'*, *'{col2}'* tiende a "
                                        f"{'aumentar' if slope > 0 else 'disminuir'} en **{abs(slope):.2f}** unidades."
                                    )
                                else:
                                    rel_type = "positive" if coef > 0 else "negative"
                                    force = "very strong" if abs(coef) >= 0.7 else "moderate"
                                    insight_text = (
                                        f"**Relationship between '{col1}' and '{col2}':** "
                                        f"There is a {force} {rel_type} linear correlation ($r = {coef:.2f}$). "
                                        f"On average, for each unit that *'{col1}'* increases, *'{col2}'* tends to "
                                        f"{'increase' if slope > 0 else 'decrease'} by **{abs(slope):.2f}** units."
                                    )
                                bivariate_insights.append({
                                    "cols": (col1, col2),
                                    "type": "correlation",
                                    "r": coef,
                                    "slope": slope,
                                    "intercept": intercept,
                                    "text": insight_text
                                })

    # 2. Categorical-Numeric Interaction Analysis
    nominal_cols = [col for col, meta in metadata.items() if meta["type"] == "Nominal"]
    quant_cols = [col for col, meta in metadata.items() if meta["type"] == "Quantitative"]
    
    # Cap processing to prevent UI freezing on wide datasets (max 15x15 = 225 combinations)
    if len(nominal_cols) > 15:
        nominal_cols = nominal_cols[:15]
    if len(quant_cols) > 15:
        quant_cols = quant_cols[:15]

    for col_name in nominal_cols:
        for num_col in quant_cols:
            grouped = df.groupby(col_name)[num_col].agg(["mean", "count"]).dropna()
            grouped = grouped[grouped["count"] >= 3]
            
            if len(grouped) >= 2:
                overall_mean = df[num_col].mean()
                max_row = grouped.loc[grouped["mean"].idxmax()]
                min_row = grouped.loc[grouped["mean"].idxmin()]
                
                max_cat = grouped["mean"].idxmax()
                min_cat = grouped["mean"].idxmin()
                
                diff_pct = ((max_row["mean"] - min_row["mean"]) / (min_row["mean"] if min_row["mean"] != 0 else 1)) * 100
                
                if diff_pct >= 15.0:
                    if lang == "es":
                        insight_text = (
                            f"**Diferencia de '{num_col}' por '{col_name}':** "
                            f"La categoría **'{max_cat}'** registra la media más alta de *'{num_col}'* con **{max_row['mean']:.2f}**, "
                            f"mientras que **'{min_cat}'** tiene la más baja con **{min_row['mean']:.2f}** "
                            f"(una diferencia relativa del {diff_pct:.1f}% entre grupos). El promedio general es {overall_mean:.2f}."
                        )
                    else:
                        insight_text = (
                            f"**Difference of '{num_col}' by '{col_name}':** "
                            f"Category **'{max_cat}'** registers the highest mean of *'{num_col}'* with **{max_row['mean']:.2f}**, "
                            f"while **'{min_cat}'** has the lowest with **{min_row['mean']:.2f}** "
                            f"(a relative difference of {diff_pct:.1f}% between groups). The overall average is {overall_mean:.2f}."
                        )
                    bivariate_insights.append({
                        "cols": (col_name, num_col),
                        "type": "aggregation",
                        "text": insight_text
                    })
                            
    return bivariate_insights
