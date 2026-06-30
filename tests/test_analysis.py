import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import analyzer
import recommender


# -------------------------------------------------------------------
# Section 1: Semantic Type Inference (extract_metadata)
# -------------------------------------------------------------------

def test_extract_metadata_continuous_numeric():
    """
    A numeric column with many distinct values must be Quantitative and NOT discrete.
    """
    df = pd.DataFrame({"Ventas": np.random.uniform(1000, 9000, 100)})
    meta = analyzer.extract_metadata(df)

    assert "Ventas" in meta
    assert meta["Ventas"]["type"] == "Quantitative"
    assert meta["Ventas"]["is_discrete"] is False
    assert "stats" in meta["Ventas"]
    assert "mean" in meta["Ventas"]["stats"]


def test_extract_metadata_discrete_numeric_preserves_ordinality():
    """
    A numeric column with <= 15 distinct integer values must be Quantitative
    but flagged as discrete=True, NOT coerced to Nominal.
    Previously (before refactor) this would have become Nominal, destroying order.
    """
    df = pd.DataFrame({"Rating": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5]})
    meta = analyzer.extract_metadata(df)

    assert "Rating" in meta
    # Must remain Quantitative to preserve mathematical ordinality
    assert meta["Rating"]["type"] == "Quantitative"
    # Must be flagged as discrete so recommender can treat it as groupable
    assert meta["Rating"]["is_discrete"] is True


def test_extract_metadata_nominal():
    """
    A string/categorical column must be classified as Nominal.
    """
    df = pd.DataFrame({
        "Producto": ["A", "B", "A", "C", "B", "A"] * 5,
    })
    meta = analyzer.extract_metadata(df)

    assert "Producto" in meta
    assert meta["Producto"]["type"] == "Nominal"
    assert meta["Producto"]["is_discrete"] is False
    assert "stats" in meta["Producto"]
    assert "top" in meta["Producto"]["stats"]


def test_extract_metadata_missing_values_insight():
    """
    Columns with missing values must generate an insight mentioning missing values.
    """
    df = pd.DataFrame({"Col": [1.0, 2.0, None, None, 5.0] * 10})
    meta = analyzer.extract_metadata(df)

    assert meta["Col"]["n_missing"] > 0
    assert any("faltantes" in ins for ins in meta["Col"]["insights"])


def test_extract_metadata_skewness_insight_symmetric():
    """
    A symmetric distribution (skewness near 0) must yield a 'simétrica' insight.
    """
    np.random.seed(42)
    df = pd.DataFrame({"Normal": np.random.normal(0, 1, 200)})
    meta = analyzer.extract_metadata(df)

    insights = meta["Normal"]["insights"]
    assert any("simétrica" in ins for ins in insights)


def test_extract_metadata_skewness_insight_positive():
    """
    A right-skewed distribution (e.g., exponential) must yield a positive skew insight.
    """
    np.random.seed(42)
    df = pd.DataFrame({"Exponencial": np.random.exponential(scale=1.0, size=200)})
    meta = analyzer.extract_metadata(df)

    insights = meta["Exponencial"]["insights"]
    assert any("positiva" in ins for ins in insights)


def test_extract_metadata_high_cardinality_insight():
    """
    A nominal column with > 15 distinct categories must flag a high cardinality warning.
    """
    categories = [f"Cat_{i}" for i in range(20)]
    df = pd.DataFrame({"Categoria": np.random.choice(categories, 100)})
    meta = analyzer.extract_metadata(df)

    assert meta["Categoria"]["type"] == "Nominal"
    insights = meta["Categoria"]["insights"]
    assert any("cardinalidad" in ins.lower() for ins in insights)


# -------------------------------------------------------------------
# Section 2: Bivariate Insights
# -------------------------------------------------------------------

def test_bivariate_correlation_pearson_detected():
    """
    A perfect linear positive correlation must be detected with r=1.0
    and slope approximately 2.0.
    """
    df = pd.DataFrame({
        "X": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
        "Y": [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0],
    })
    metadata = {
        "X": {"type": "Quantitative", "is_discrete": False},
        "Y": {"type": "Quantitative", "is_discrete": False},
    }

    bivariate = analyzer.calculate_bivariate_insights(df, metadata)

    corrs = [b for b in bivariate if b["type"] == "correlation"]
    assert len(corrs) == 1
    assert corrs[0]["r"] == pytest.approx(1.0, abs=0.01)
    assert corrs[0]["slope"] == pytest.approx(2.0, abs=0.01)
    assert "muy fuerte" in corrs[0]["text"]


def test_bivariate_correlation_below_threshold_not_reported():
    """
    A near-zero correlation (noise) must not generate a correlation insight.
    """
    np.random.seed(0)
    df = pd.DataFrame({
        "X": np.random.normal(0, 1, 50),
        "Y": np.random.normal(0, 1, 50),
    })
    metadata = {
        "X": {"type": "Quantitative", "is_discrete": False},
        "Y": {"type": "Quantitative", "is_discrete": False},
    }

    bivariate = analyzer.calculate_bivariate_insights(df, metadata)
    corrs = [b for b in bivariate if b["type"] == "correlation"]
    # May or may not fire depending on random seed, but if it does fire, r must be >= 0.35
    for c in corrs:
        assert abs(c["r"]) >= 0.35


def test_bivariate_aggregation_effect_size_detected():
    """
    Two groups with a large mean difference (effect size >= 0.5) must generate an
    aggregation insight. Uses the new Cohen's d variant instead of the old
    fragile percentage-based formula.
    """
    # Group A ~ 10, Group B ~ 100 — very large effect size
    df = pd.DataFrame({
        "Categoria": ["A"] * 10 + ["B"] * 10,
        "Valor": [10, 11, 9, 12, 10, 11, 9, 10, 11, 10,
                  100, 101, 99, 102, 100, 101, 99, 100, 101, 100],
    })
    metadata = {
        "Categoria": {"type": "Nominal", "is_discrete": False, "n_distinct": 2},
        "Valor": {"type": "Quantitative", "is_discrete": False},
    }

    bivariate = analyzer.calculate_bivariate_insights(df, metadata)
    aggs = [b for b in bivariate if b["type"] == "aggregation"]

    assert len(aggs) == 1
    assert "Categoria" in aggs[0]["cols"]
    assert "Valor" in aggs[0]["cols"]
    # New insight text uses "efecto" instead of old "diferencia relativa"
    assert "efecto" in aggs[0]["text"].lower()


def test_bivariate_aggregation_no_division_by_zero():
    """
    When the min group mean is zero, the old (max-min)/min formula would
    divide by zero. The new effect size formula must handle this gracefully.
    """
    df = pd.DataFrame({
        "Cat": ["A"] * 10 + ["B"] * 10,
        "Val": [0.0] * 10 + [50.0] * 10,
    })
    metadata = {
        "Cat": {"type": "Nominal", "is_discrete": False, "n_distinct": 2},
        "Val": {"type": "Quantitative", "is_discrete": False},
    }

    # Must not raise any exception
    bivariate = analyzer.calculate_bivariate_insights(df, metadata)
    aggs = [b for b in bivariate if b["type"] == "aggregation"]
    # The effect size is (50-0)/std which should be large enough to trigger
    assert len(aggs) == 1


def test_bivariate_aggregation_min_count_filter():
    """
    Groups with fewer than 5 observations must be excluded from aggregation analysis.
    With only 2 obs per group, no insight should be generated.
    """
    df = pd.DataFrame({
        "Cat": ["A", "A", "B", "B"],
        "Val": [10.0, 11.0, 100.0, 101.0],
    })
    metadata = {
        "Cat": {"type": "Nominal", "is_discrete": False, "n_distinct": 2},
        "Val": {"type": "Quantitative", "is_discrete": False},
    }

    bivariate = analyzer.calculate_bivariate_insights(df, metadata)
    aggs = [b for b in bivariate if b["type"] == "aggregation"]
    # Groups have n=2 < 5 minimum, so no insight should fire
    assert len(aggs) == 0


# -------------------------------------------------------------------
# Section 3: Chart Recommender
# -------------------------------------------------------------------

def test_recommender_scatter_priority_above_temporal():
    """
    A strong correlation (r=0.85, small dataset) should produce a scatter plot
    with priority > 85 (higher than the temporal line chart default).
    """
    metadata = {
        "Ventas": {"type": "Quantitative", "is_discrete": False, "n_distinct": 50,
                   "n_rows": 100, "insights": [], "stats": {}},
        "Gastos": {"type": "Quantitative", "is_discrete": False, "n_distinct": 50,
                   "n_rows": 100, "insights": [], "stats": {}},
        "Fecha":  {"type": "Temporal",     "is_discrete": False, "n_distinct": 100,
                   "n_rows": 100, "insights": []},
    }
    bivariate_insights = [{
        "cols": ("Ventas", "Gastos"),
        "type": "correlation",
        "r": 0.85,
        "is_nonlinear": False,
        "text": "Fuerte correlación",
    }]

    recs = recommender.recommend_charts(metadata, bivariate_insights)

    assert len(recs) > 0
    assert recs[0]["chart_type"] == "scatter"
    assert recs[0]["priority"] > 85


def test_recommender_density_heatmap_for_large_datasets():
    """
    For datasets with N > 5000, the recommender must suggest a density heatmap
    instead of a regular scatter plot to prevent overplotting.
    """
    metadata = {
        "X": {"type": "Quantitative", "is_discrete": False, "n_distinct": 5001,
              "n_rows": 6000, "insights": [], "stats": {}},
        "Y": {"type": "Quantitative", "is_discrete": False, "n_distinct": 5001,
              "n_rows": 6000, "insights": [], "stats": {}},
    }
    bivariate_insights = [{
        "cols": ("X", "Y"),
        "type": "correlation",
        "r": 0.75,
        "is_nonlinear": False,
        "text": "Correlación fuerte",
    }]

    recs = recommender.recommend_charts(metadata, bivariate_insights)
    scatter_types = [r["chart_type"] for r in recs]

    assert "density_heatmap" in scatter_types
    assert "scatter" not in scatter_types


def test_recommender_boxplot_priority_above_bar_aggregation():
    """
    Segmented boxplots (Priority 75) must appear before bar aggregations (Priority 60)
    for categorical vs numeric group comparisons.
    This is the fix for the 'dynamite plot' anti-pattern.
    """
    metadata = {
        "Categoria": {"type": "Nominal", "is_discrete": False, "n_distinct": 3,
                      "n_rows": 100, "insights": []},
        "Valor": {"type": "Quantitative", "is_discrete": False, "n_distinct": 50,
                  "n_rows": 100, "insights": [], "stats": {}},
    }
    bivariate_insights = [{
        "cols": ("Categoria", "Valor"),
        "type": "aggregation",
        "text": "Diferencia significativa",
    }]

    recs = recommender.recommend_charts(metadata, bivariate_insights)

    chart_types = [r["chart_type"] for r in recs]
    assert "boxplot_segmented" in chart_types
    assert "bar_aggregation" in chart_types

    boxplot_idx = chart_types.index("boxplot_segmented")
    bar_idx = chart_types.index("bar_aggregation")
    assert boxplot_idx < bar_idx, "Boxplot should appear before bar_aggregation (higher priority)"


def test_recommender_no_pie_for_more_than_3_categories():
    """
    Pie charts must NOT be recommended if there are more than 3 categories.
    Bar charts must be used instead.
    """
    metadata = {
        "Producto": {"type": "Nominal", "is_discrete": False, "n_distinct": 5,
                     "n_rows": 100, "insights": []},
    }

    recs = recommender.recommend_charts(metadata, [])

    chart_types = [r["chart_type"] for r in recs]
    assert "pie" not in chart_types
    assert "bar_frequency" in chart_types


def test_recommender_pie_only_allowed_for_3_or_fewer_categories():
    """
    Pie charts are only acceptable for <= 3 categories (and must have low priority).
    """
    metadata = {
        "Estado": {"type": "Nominal", "is_discrete": False, "n_distinct": 2,
                   "n_rows": 100, "insights": []},
    }

    recs = recommender.recommend_charts(metadata, [])

    pie_recs = [r for r in recs if r["chart_type"] == "pie"]
    if pie_recs:
        assert pie_recs[0]["priority"] <= 30, "Pie chart must have low priority (<= 30)"


def test_recommender_high_cardinality_uses_horizontal_bar():
    """
    Nominal columns with more than 12 unique categories must use horizontal bar charts.
    """
    metadata = {
        "Ciudad": {"type": "Nominal", "is_discrete": False, "n_distinct": 15,
                   "n_rows": 200, "insights": []},
    }

    recs = recommender.recommend_charts(metadata, [])

    chart_types = [r["chart_type"] for r in recs]
    assert "bar_horizontal" in chart_types
    assert "bar_frequency" not in chart_types


def test_recommender_sorted_by_priority_descending():
    """
    All recommendations must be sorted by priority in descending order.
    """
    metadata = {
        "Fecha":      {"type": "Temporal",     "is_discrete": False, "n_distinct": 50,
                       "n_rows": 100, "insights": []},
        "Categoria":  {"type": "Nominal",      "is_discrete": False, "n_distinct": 4,
                       "n_rows": 100, "insights": []},
        "Ventas":     {"type": "Quantitative", "is_discrete": False, "n_distinct": 50,
                       "n_rows": 100, "insights": [], "stats": {"skewness": 0.1}},
        "Gastos":     {"type": "Quantitative", "is_discrete": False, "n_distinct": 50,
                       "n_rows": 100, "insights": [], "stats": {"skewness": 0.3}},
    }
    bivariate_insights = [{
        "cols": ("Ventas", "Gastos"),
        "type": "correlation",
        "r": 0.80,
        "is_nonlinear": False,
        "text": "Correlación fuerte",
    }]

    recs = recommender.recommend_charts(metadata, bivariate_insights)

    priorities = [r["priority"] for r in recs]
    assert priorities == sorted(priorities, reverse=True), \
        "Recommendations must be in descending priority order"
