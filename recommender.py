def recommend_charts(metadata: dict, bivariate_insights: list, lang: str = "es") -> list:
    """
    Evaluates metadata structure and cross-calculated bivariate insights to
    generate a ranked list of recommended charts with justifications and priorities
    in the specified language (es/en).
    """
    recommendations = []
    
    # 1. Recommendations based on Numeric Correlations (High Priority)
    for insight in bivariate_insights:
        if insight["type"] == "correlation":
            col1, col2 = insight["cols"]
            r_val = insight["r"]
            abs_r = abs(r_val)
            
            priority = int(80 + (abs_r * 20))
            
            if lang == "es":
                title_text = f"Relación entre {col1} y {col2}"
                rationale_text = (
                    f"Existe una correlación lineal {'positiva' if r_val > 0 else 'negativa'} "
                    f"{'muy fuerte' if abs_r >= 0.7 else 'moderada'} ($r = {r_val:.2f}$) entre ambas variables. "
                    f"El gráfico de dispersión con recta de regresión permite visualizar la tendencia directamente."
                )
            else:
                title_text = f"Relationship between {col1} and {col2}"
                rationale_text = (
                    f"There is a {'very strong' if abs_r >= 0.7 else 'moderate'} "
                    f"{'positive' if r_val > 0 else 'negative'} linear correlation ($r = {r_val:.2f}$) between both variables. "
                    f"The scatter plot with regression line allows direct visualization of the trend."
                )
                
            recommendations.append({
                "chart_type": "scatter",
                "title": title_text,
                "x": col1,
                "y": col2,
                "color_by": None,
                "rationale": rationale_text,
                "insights": [insight["text"]],
                "priority": priority
            })

    # 2. Recommendations based on Temporal Trends (High Priority)
    temporal_cols = [col for col, meta in metadata.items() if meta["type"] == "Temporal"]
    numeric_cols = [col for col, meta in metadata.items() if meta["type"] == "Quantitative"]
    nominal_cols = [col for col, meta in metadata.items() if meta["type"] == "Nominal"]
    
    for t_col in temporal_cols:
        for n_col in numeric_cols:
            if lang == "es":
                title_text = f"Evolución de {n_col} a lo largo del tiempo ({t_col})"
                rationale_text = (
                    f"Muestra la trayectoria de *'{n_col}'* a través del eje temporal *'{t_col}'*. "
                    f"Es el formato ideal para identificar patrones de crecimiento, estacionalidades o tendencias de ciclo."
                )
                insight_item = f"Línea temporal sugerida para analizar la evolución histórica de '{n_col}'."
            else:
                title_text = f"Evolution of {n_col} over time ({t_col})"
                rationale_text = (
                    f"Shows the trajectory of *'{n_col}'* across the temporal axis *'{t_col}'*. "
                    f"It is the ideal format to identify growth patterns, seasonalities, or cycle trends."
                )
                insight_item = f"Suggested temporal line to analyze the historical evolution of '{n_col}'."
                
            recommendations.append({
                "chart_type": "line",
                "title": title_text,
                "x": t_col,
                "y": n_col,
                "color_by": None,
                "rationale": rationale_text,
                "insights": [insight_item],
                "priority": 85
            })

    # 3. Recommendations based on Group Mean Differences (Categorical vs Numeric)
    for insight in bivariate_insights:
        if insight["type"] == "aggregation":
            col_cat, col_num = insight["cols"]
            cardinality = metadata[col_cat]["n_distinct"]
            
            if cardinality <= 15:
                if lang == "es":
                    title_agg = f"Promedio de {col_num} por Categoría de {col_cat}"
                    rationale_agg = (
                        f"Compara los valores agregados (promedios) de la variable numérica *'{col_num}'* "
                        f"segmentados por el campo categórico *'{col_cat}'*. "
                        f"Permite comprobar qué grupos sobresalen respecto al promedio general."
                    )
                else:
                    title_agg = f"Average of {col_num} by {col_cat} Category"
                    rationale_agg = (
                        f"Compares the aggregated values (means) of the numerical variable *'{col_num}'* "
                        f"segmented by the categorical field *'{col_cat}'*. "
                        f"Allows verifying which groups stand out compared to the overall average."
                    )
                    
                recommendations.append({
                    "chart_type": "bar_aggregation",
                    "title": title_agg,
                    "x": col_cat,
                    "y": col_num,
                    "color_by": col_cat,
                    "rationale": rationale_agg,
                    "insights": [insight["text"]],
                    "priority": 70
                })
                
                if lang == "es":
                    title_box = f"Distribución de {col_num} dentro de cada {col_cat}"
                    rationale_box = (
                        f"Un diagrama de caja segmentado ayuda a comparar el rango, la mediana y la presencia "
                        f"de outliers del campo *'{col_num}'* de manera individualizada para cada categoría de *'{col_cat}'*."
                    )
                    insight_box = f"Permite verificar si la dispersión o variabilidad de '{col_num}' difiere según el grupo de '{col_cat}'."
                else:
                    title_box = f"Distribution of {col_num} within each {col_cat}"
                    rationale_box = (
                        f"A segmented boxplot helps compare the range, median, and presence "
                        f"of outliers of the field *'{col_num}'* individually for each category of *'{col_cat}'*."
                    )
                    insight_box = f"Allows verifying if the dispersion or variability of '{col_num}' differs by the group of '{col_cat}'."
                    
                recommendations.append({
                    "chart_type": "boxplot_segmented",
                    "title": title_box,
                    "x": col_cat,
                    "y": col_num,
                    "color_by": col_cat,
                    "rationale": rationale_box,
                    "insights": [insight_box],
                    "priority": 65
                })

    # 4. Univariate Recommendations (1 Numeric Variable)
    for col in numeric_cols:
        meta = metadata[col]
        stats = meta.get("stats", {})
        skewness = stats.get("skewness", 0)
        
        if lang == "es":
            title_hist = f"Distribución de {col}"
            rationale_hist = (
                f"Muestra la frecuencia con la que ocurren los valores en *'{col}'*. "
                f"Con un sesgo de {skewness:.2f}, el histograma es fundamental para evaluar si la muestra "
                f"sigue una distribución normal o tiene asimetrías."
            )
        else:
            title_hist = f"Distribution of {col}"
            rationale_hist = (
                f"Shows the frequency with which values occur in *'{col}'*. "
                f"With a skewness of {skewness:.2f}, the histogram is key to evaluate if the sample "
                f"follows a normal distribution or has asymmetries."
            )
            
        recommendations.append({
            "chart_type": "histogram",
            "title": title_hist,
            "x": col,
            "y": None,
            "color_by": None,
            "rationale": rationale_hist,
            "insights": meta["insights"],
            "priority": 50
        })
        
        if lang == "es":
            title_box_uni = f"Caja y Bigotes (Outliers) de {col}"
            rationale_box_uni = (
                f"El diagrama de caja y bigotes es la mejor visualización determinista para inspeccionar "
                f"el rango intercuartílico (IQR), la mediana, la simetría y para identificar visualmente "
                f"los valores atípicos (outliers) en *'{col}'*."
            )
        else:
            title_box_uni = f"Box and Whiskers (Outliers) of {col}"
            rationale_box_uni = (
                f"The box and whiskers plot is the best deterministic visualization to inspect "
                f"the interquartile range (IQR), median, symmetry, and to visually identify "
                f"outliers in *'{col}'*."
            )
            
        recommendations.append({
            "chart_type": "boxplot",
            "title": title_box_uni,
            "x": col,
            "y": None,
            "color_by": None,
            "rationale": rationale_box_uni,
            "insights": meta["insights"],
            "priority": 45
        })

    # 5. Univariate Recommendations (1 Categorical Variable)
    for col in nominal_cols:
        meta = metadata[col]
        cardinality = meta["n_distinct"]
        
        if cardinality <= 15:
            chart_t = "pie" if cardinality <= 5 else "bar_frequency"
            if lang == "es":
                title_nom = f"Distribución de Categorías en {col}"
                rationale_nom = (
                    f"Representa el conteo de frecuencia de las {cardinality} categorías de *'{col}'*. "
                    f"Ideal para ver la proporción y el dominio de los valores más comunes en la muestra."
                )
            else:
                title_nom = f"Category Distribution in {col}"
                rationale_nom = (
                    f"Represents the frequency count of the {cardinality} categories of *'{col}'*. "
                    f"Ideal to see the proportion and dominance of the most common values in the sample."
                )
                
            recommendations.append({
                "chart_type": chart_t,
                "title": title_nom,
                "x": col,
                "y": None,
                "color_by": col if chart_t == "pie" else None,
                "rationale": rationale_nom,
                "insights": meta["insights"],
                "priority": 40
            })
        else:
            if lang == "es":
                title_nom_high = f"Frecuencias de {col} (Alta Cardinalidad)"
                rationale_nom_high = (
                    f"Debido a que *'{col}'* posee {cardinality} categorías únicas, se sugiere un gráfico "
                    f"de barras horizontales ordenado para permitir una lectura clara sin superposición de texto."
                )
            else:
                title_nom_high = f"Frequencies of {col} (High Cardinality)"
                rationale_nom_high = (
                    f"Since *'{col}'* has {cardinality} unique categories, a sorted horizontal bar chart "
                    f"is suggested to allow a clear read without overlapping text."
                )
                
            recommendations.append({
                "chart_type": "bar_horizontal",
                "title": title_nom_high,
                "x": col,
                "y": None,
                "color_by": None,
                "rationale": rationale_nom_high,
                "insights": meta["insights"],
                "priority": 35
            })
            
    recommendations.sort(key=lambda r: r["priority"], reverse=True)
    return recommendations
