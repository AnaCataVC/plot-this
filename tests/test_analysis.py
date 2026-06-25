import pytest
import pandas as pd
import numpy as np
import analyzer
import recommender

# Simple Mock class to simulate ydata-profiling's BaseDescription structure
class MockBaseDescription:
    def __init__(self, variables, table):
        self.variables = variables
        self.table = table

def test_get_simplified_type():
    """
    Verifies that the type mapping logic maps ydata-profiling types
    correctly and applies cardinality coercion for discrete numerics.
    """
    # Standard mappings
    assert analyzer.get_simplified_type("Numeric", 50) == "Quantitative"
    assert analyzer.get_simplified_type("Categorical", 12) == "Nominal"
    assert analyzer.get_simplified_type("Boolean", 2) == "Nominal"
    assert analyzer.get_simplified_type("DateTime", 100) == "Temporal"
    
    # Cardinality coercion: numeric with low cardinality (< 10) maps to Nominal
    assert analyzer.get_simplified_type("Numeric", 5) == "Nominal"

def test_extract_metadata_numeric():
    """
    Validates univariate metadata extraction for continuous quantitative columns.
    """
    mock_variables = {
        "Ventas": {
            "type": "Numeric",
            "n_distinct": 25,
            "n_missing": 0,
            "p_missing": 0.0,
            "mean": 5000.0,
            "50%": 4800.0,
            "std": 1200.0,
            "min": 1000.0,
            "max": 9000.0,
            "skewness": 0.2, # Symmetric distribution
            "iqr": 2000.0,
            "25%": 3800.0,
            "75%": 5800.0
        }
    }
    mock_desc = MockBaseDescription(mock_variables, {"n": 100})
    
    meta = analyzer.extract_metadata(mock_desc)
    
    assert "Ventas" in meta
    assert meta["Ventas"]["type"] == "Quantitative"
    assert meta["Ventas"]["stats"]["mean"] == 5000.0
    assert meta["Ventas"]["stats"]["median"] == 4800.0
    
    # Verifies that it suggests a symmetric distribution insight based on skewness = 0.2
    insights = meta["Ventas"]["insights"]
    assert any("simétrica" in ins for ins in insights)

def test_extract_metadata_nominal():
    """
    Validates univariate metadata extraction for categorical (nominal) columns.
    """
    mock_variables = {
        "Producto": {
            "type": "Categorical",
            "n_distinct": 3,
            "n_missing": 2,
            "p_missing": 0.02,
            "top": "Tecnologia",
            "freq": 60
        }
    }
    # n total = 100
    mock_desc = MockBaseDescription(mock_variables, {"n": 100})
    
    meta = analyzer.extract_metadata(mock_desc)
    
    assert "Producto" in meta
    assert meta["Producto"]["type"] == "Nominal"
    assert meta["Producto"]["stats"]["top"] == "Tecnologia"
    
    insights = meta["Producto"]["insights"]
    # Verifies that it raises a missing values alert
    assert any("valores faltantes" in ins for ins in insights)
    # Verifies that it identifies the dominant value
    assert any("dominante" in ins for ins in insights)

def test_calculate_bivariate_insights_correlation():
    """
    Validates linear correlation coefficient and regression line math.
    """
    # Create DataFrame with perfect positive linear correlation
    df = pd.DataFrame({
        "X": [1, 2, 3, 4, 5, 6, 7, 8],
        "Y": [2, 4, 6, 8, 10, 12, 14, 16]
    })
    
    metadata = {
        "X": {"type": "Quantitative"},
        "Y": {"type": "Quantitative"}
    }
    
    # Pass empty MockBaseDescription since correlations are computed directly from df
    mock_desc = MockBaseDescription({}, {})
    
    bivariate = analyzer.calculate_bivariate_insights(df, metadata, mock_desc)
    
    # Verifies that it detects the correlation
    corrs = [b for b in bivariate if b["type"] == "correlation"]
    assert len(corrs) == 1
    assert corrs[0]["r"] == pytest.approx(1.0)
    assert corrs[0]["slope"] == pytest.approx(2.0)
    assert "muy fuerte" in corrs[0]["text"]

def test_calculate_bivariate_insights_aggregation():
    """
    Validates mean differences calculations between nominal and numeric variables.
    """
    df = pd.DataFrame({
        "Categoria": ["A", "A", "A", "B", "B", "B"],
        "Valor": [10, 12, 11, 100, 105, 95] # Group B has significantly higher values
    })
    
    metadata = {
        "Categoria": {"type": "Nominal", "n_distinct": 2},
        "Valor": {"type": "Quantitative"}
    }
    
    mock_desc = MockBaseDescription({}, {})
    
    bivariate = analyzer.calculate_bivariate_insights(df, metadata, mock_desc)
    
    aggregations = [b for b in bivariate if b["type"] == "aggregation"]
    assert len(aggregations) == 1
    assert "Categoria" in aggregations[0]["cols"]
    assert "Valor" in aggregations[0]["cols"]
    assert "diferencia relativa" in aggregations[0]["text"]

def test_recommend_charts():
    """
    Verifies that the recommendation logic maps variables structures
    correctly and sorts recommendations by priority.
    """
    metadata = {
        "Fecha": {"type": "Temporal", "n_distinct": 10, "insights": []},
        "Categoria": {"type": "Nominal", "n_distinct": 3, "insights": ["🏷️ Insight"]},
        "Ventas": {"type": "Quantitative", "insights": ["📊 Insight"]},
        "Gastos": {"type": "Quantitative", "insights": []}
    }
    
    bivariate_insights = [
        {
            "cols": ("Ventas", "Gastos"),
            "type": "correlation",
            "r": 0.85,
            "text": "🔗 Fuerte correlación"
        },
        {
            "cols": ("Categoria", "Ventas"),
            "type": "aggregation",
            "text": "🏷️📊 Diferencia de medias"
        }
    ]
    
    recs = recommender.recommend_charts(metadata, bivariate_insights)
    
    # Verify recommendations are not empty
    assert len(recs) > 0
    
    # First recommendation should be the correlation scatter plot of Ventas vs Gastos
    assert recs[0]["chart_type"] == "scatter"
    assert recs[0]["x"] == "Ventas"
    assert recs[0]["y"] == "Gastos"
    
    # Verify it recommends temporal line charts for both numerical columns
    lines = [r for r in recs if r["chart_type"] == "line"]
    assert len(lines) == 2
    assert any(l["x"] == "Fecha" and l["y"] == "Ventas" for l in lines)
