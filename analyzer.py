import pandas as pd
import numpy as np
from ydata_profiling import ProfileReport

def analyze_dataset(df: pd.DataFrame) -> object:
    """
    Runs ydata-profiling in-memory in minimal mode and extracts the
    complete statistical description object (BaseDescription).
    """
    # Execute with minimal=True for maximum in-memory speed
    profile = ProfileReport(df, minimal=True, progress_bar=False)
    desc = profile.get_description()
    return desc

def get_simplified_type(ydata_type: str, cardinality: int) -> str:
    """
    Maps semantic types from ydata-profiling to simplified types (Q, N, T)
    with cardinality coercion for discrete numeric fields.
    """
    ydata_type = str(ydata_type).lower()
    
    if "numeric" in ydata_type:
        # Cardinality coercion: if a numeric column has less than 10 unique values,
        # treat it as Categorical (Nominal) to facilitate aggregate calculations.
        if cardinality < 10:
            return "Nominal"
        return "Quantitative"
    elif "datetime" in ydata_type:
        return "Temporal"
    elif "categorical" in ydata_type or "boolean" in ydata_type:
        return "Nominal"
    else:
        return "Nominal"  # Default type

def extract_metadata(desc: object, lang: str = "es") -> dict:
    """
    Parses ydata-profiling's BaseDescription object to extract a clean structure
    of columns, types, and basic univariate insights in the specified language (es/en).
    """
    metadata = {}
    variables = desc.variables
    table = desc.table
    
    for col, info in variables.items():
        orig_type = info.get("type", "Categorical")
        n_distinct = info.get("n_distinct", 0)
        n_missing = info.get("n_missing", 0)
        p_missing = info.get("p_missing", 0.0)
        
        simple_type = get_simplified_type(orig_type, n_distinct)
        
        col_meta = {
            "name": col,
            "original_type": orig_type,
            "type": simple_type,
            "n_distinct": n_distinct,
            "n_missing": n_missing,
            "p_missing": p_missing,
            "insights": []
        }
        
        # Univariate deterministic insights generation
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
            mean_val = info.get("mean", 0)
            median_val = info.get("50%", 0)
            std_val = info.get("std", 0)
            skewness = info.get("skewness", 0)
            iqr = info.get("iqr", 0)
            
            col_meta["stats"] = {
                "mean": mean_val,
                "median": median_val,
                "std": std_val,
                "min": info.get("min", 0),
                "max": info.get("max", 0),
                "skewness": skewness,
                "iqr": iqr
            }
            
            # Skewness / distribution symmetry insights
            if abs(skewness) < 0.5:
                if lang == "es":
                    col_meta["insights"].append(
                        f"La distribución es relativamente simétrica (sesgo: {skewness:.2f})."
                    )
                else:
                    col_meta["insights"].append(
                        f"The distribution is relatively symmetric (skewness: {skewness:.2f})."
                    )
            elif skewness >= 0.5:
                if lang == "es":
                    col_meta["insights"].append(
                        f"La distribución presenta asimetría positiva a la derecha (sesgo: {skewness:.2f}), sugiriendo una concentración en valores más bajos."
                    )
                else:
                    col_meta["insights"].append(
                        f"The distribution shows positive right skewness (skewness: {skewness:.2f}), suggesting concentration in lower values."
                    )
            else:
                if lang == "es":
                    col_meta["insights"].append(
                        f"La distribución presenta asimetría negativa a la izquierda (sesgo: {skewness:.2f}), sugiriendo concentración en valores altos."
                    )
                else:
                    col_meta["insights"].append(
                        f"The distribution shows negative left skewness (skewness: {skewness:.2f}), suggesting concentration in higher values."
                    )
                
            # Outlier detection using IQR
            if iqr > 0:
                q1 = info.get("25%", 0)
                q3 = info.get("75%", 0)
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                col_meta["stats"]["outlier_bounds"] = (lower_bound, upper_bound)
                
        elif simple_type == "Nominal":
            col_meta["stats"] = {
                "top": info.get("top", "N/A"),
                "freq": info.get("freq", 0),
            }
            top_val = info.get("top", "N/A")
            freq_val = info.get("freq", 0)
            total_obs = table.get("n", 1)
            
            if freq_val > 0 and total_obs > 0:
                pct = (freq_val / total_obs) * 100
                if lang == "es":
                    col_meta["insights"].append(
                        f"El valor dominante es **'{top_val}'**, representando el {pct:.1f}% de las filas ({freq_val} apariciones)."
                    )
                else:
                    col_meta["insights"].append(
                        f"The dominant value is **'{top_val}'**, representing {pct:.1f}% of rows ({freq_val} occurrences)."
                    )
                
            if n_distinct > 15:
                if lang == "es":
                    col_meta["insights"].append(
                        f"Alta cardinalidad ({n_distinct} categorías únicas). Se sugiere agrupar categorías menores al graficar."
                    )
                else:
                    col_meta["insights"].append(
                        f"High cardinality ({n_distinct} unique categories). Suggest grouping smaller categories when plotting."
                    )
                
        metadata[col] = col_meta
        
    return metadata

def calculate_bivariate_insights(df: pd.DataFrame, metadata: dict, desc: object, lang: str = "es") -> list:
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
    for col_name, meta in metadata.items():
        if meta["type"] == "Nominal":
            for num_col, num_meta in metadata.items():
                if num_meta["type"] == "Quantitative":
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
