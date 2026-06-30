"""
run_tests.py — Lightweight standalone test runner for plot-this.
Uses Python's unittest framework to avoid dependency on the global pytest
environment, which is broken by a missing pydantic dependency in langsmith.
"""
import sys
import os
import unittest

# Ensure project root is on path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
import analyzer
import recommender


class TestSemanticTypeInference(unittest.TestCase):
    """Tests for extract_metadata type classification logic."""

    def test_continuous_numeric_is_quantitative_not_discrete(self):
        """Continuous numeric columns must be Quantitative and NOT discrete."""
        df = pd.DataFrame({"Ventas": np.random.uniform(1000, 9000, 100)})
        meta = analyzer.extract_metadata(df)
        self.assertEqual(meta["Ventas"]["type"], "Quantitative")
        self.assertFalse(meta["Ventas"]["is_discrete"])
        self.assertIn("stats", meta["Ventas"])
        self.assertIn("mean", meta["Ventas"]["stats"])

    def test_discrete_numeric_preserves_ordinality(self):
        """
        A numeric column with <= 15 distinct values must remain Quantitative
        (not coerced to Nominal) but be flagged as is_discrete=True.
        This preserves mathematical ordering on chart axes.
        """
        df = pd.DataFrame({"Rating": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5]})
        meta = analyzer.extract_metadata(df)
        self.assertEqual(meta["Rating"]["type"], "Quantitative",
                         "Discrete numeric must remain Quantitative, not Nominal")
        self.assertTrue(meta["Rating"]["is_discrete"],
                        "Discrete numeric must be flagged with is_discrete=True")

    def test_string_column_is_nominal(self):
        """String columns must be classified as Nominal."""
        df = pd.DataFrame({"Producto": ["A", "B", "A", "C", "B", "A"] * 5})
        meta = analyzer.extract_metadata(df)
        self.assertEqual(meta["Producto"]["type"], "Nominal")
        self.assertFalse(meta["Producto"]["is_discrete"])
        self.assertIn("top", meta["Producto"]["stats"])

    def test_missing_values_insight_generated(self):
        """Columns with nulls must generate a 'faltantes' insight."""
        df = pd.DataFrame({"Col": [1.0, 2.0, None, None, 5.0] * 10})
        meta = analyzer.extract_metadata(df)
        self.assertGreater(meta["Col"]["n_missing"], 0)
        self.assertTrue(any("faltantes" in ins for ins in meta["Col"]["insights"]))

    def test_symmetric_distribution_insight(self):
        """A near-normal distribution must yield a 'simétrica' insight."""
        np.random.seed(42)
        df = pd.DataFrame({"Normal": np.random.normal(0, 1, 200)})
        meta = analyzer.extract_metadata(df)
        self.assertTrue(any("simétrica" in ins for ins in meta["Normal"]["insights"]))

    def test_right_skewed_distribution_insight(self):
        """An exponential (right-skewed) distribution must yield a positive skew insight."""
        np.random.seed(42)
        df = pd.DataFrame({"Expo": np.random.exponential(scale=1.0, size=300)})
        meta = analyzer.extract_metadata(df)
        self.assertTrue(any("positiva" in ins for ins in meta["Expo"]["insights"]))

    def test_high_cardinality_nominal_warns(self):
        """Nominal with > 15 categories must raise a cardinality warning insight."""
        cats = [f"Cat_{i}" for i in range(20)]
        df = pd.DataFrame({"Categoria": np.random.choice(cats, 100)})
        meta = analyzer.extract_metadata(df)
        self.assertEqual(meta["Categoria"]["type"], "Nominal")
        self.assertTrue(any("cardinalidad" in ins.lower() for ins in meta["Categoria"]["insights"]))


class TestBivariateInsights(unittest.TestCase):
    """Tests for calculate_bivariate_insights() math and thresholds."""

    def test_perfect_linear_correlation_detected(self):
        """Perfect positive linear correlation (r=1.0) must be captured with slope=2.0."""
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
        self.assertEqual(len(corrs), 1)
        self.assertAlmostEqual(corrs[0]["r"], 1.0, places=2)
        self.assertAlmostEqual(corrs[0]["slope"], 2.0, places=2)
        self.assertIn("muy fuerte", corrs[0]["text"])

    def test_correlation_below_threshold_not_reported(self):
        """Near-zero correlations (random noise) must not generate insights."""
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
        for c in corrs:
            self.assertGreaterEqual(abs(c["r"]), 0.35,
                                    "Only correlations >= 0.35 should be reported")

    def test_effect_size_aggregation_detected(self):
        """Two clearly separated groups (high effect size d) must generate an aggregation insight."""
        df = pd.DataFrame({
            "Cat": ["A"] * 10 + ["B"] * 10,
            "Val": [10, 11, 9, 12, 10, 11, 9, 10, 11, 10,
                    100, 101, 99, 102, 100, 101, 99, 100, 101, 100],
        })
        metadata = {
            "Cat": {"type": "Nominal", "is_discrete": False, "n_distinct": 2},
            "Val": {"type": "Quantitative", "is_discrete": False},
        }
        bivariate = analyzer.calculate_bivariate_insights(df, metadata)
        aggs = [b for b in bivariate if b["type"] == "aggregation"]
        self.assertEqual(len(aggs), 1)
        self.assertIn("Cat", aggs[0]["cols"])
        self.assertIn("Val", aggs[0]["cols"])
        # New metric: uses "efecto" not "diferencia relativa"
        self.assertIn("efecto", aggs[0]["text"].lower())

    def test_aggregation_no_division_by_zero_with_zero_min_group(self):
        """When min group mean is 0.0, the effect size formula must not raise ZeroDivisionError."""
        df = pd.DataFrame({
            "Cat": ["A"] * 10 + ["B"] * 10,
            "Val": [0.0] * 10 + [50.0] * 10,
        })
        metadata = {
            "Cat": {"type": "Nominal", "is_discrete": False, "n_distinct": 2},
            "Val": {"type": "Quantitative", "is_discrete": False},
        }
        try:
            bivariate = analyzer.calculate_bivariate_insights(df, metadata)
            aggs = [b for b in bivariate if b["type"] == "aggregation"]
            self.assertEqual(len(aggs), 1, "Large separation (d >> 0.5) should fire")
        except ZeroDivisionError:
            self.fail("Division by zero: old (max-min)/min formula still active!")

    def test_aggregation_min_count_filter_prevents_small_groups(self):
        """Groups with < 5 observations must be filtered out (no insights)."""
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
        self.assertEqual(len(aggs), 0, "Groups with n<5 should not generate insights")


class TestChartRecommender(unittest.TestCase):
    """Tests for recommend_charts() priorities and chart-type selection."""

    def _base_meta(self, col_type, n_distinct, n_rows=100, is_discrete=False):
        m = {"type": col_type, "is_discrete": is_discrete,
             "n_distinct": n_distinct, "n_rows": n_rows, "insights": []}
        if col_type == "Quantitative":
            m["stats"] = {"skewness": 0.1}
        return m

    def test_scatter_priority_above_85_for_strong_correlation(self):
        """A strong correlation on a small dataset must produce scatter with priority > 85."""
        metadata = {
            "Ventas": self._base_meta("Quantitative", 50),
            "Gastos": self._base_meta("Quantitative", 50),
            "Fecha":  {"type": "Temporal", "is_discrete": False,
                       "n_distinct": 100, "n_rows": 100, "insights": []},
        }
        insights = [{"cols": ("Ventas", "Gastos"), "type": "correlation",
                     "r": 0.85, "is_nonlinear": False, "text": "Fuerte"}]
        recs = recommender.recommend_charts(metadata, insights)
        self.assertGreater(len(recs), 0)
        self.assertEqual(recs[0]["chart_type"], "scatter")
        self.assertGreater(recs[0]["priority"], 85)

    def test_density_heatmap_replaces_scatter_for_large_datasets(self):
        """For N > 5000 rows, density heatmap must be recommended instead of scatter."""
        metadata = {
            "X": self._base_meta("Quantitative", 5001, n_rows=6000),
            "Y": self._base_meta("Quantitative", 5001, n_rows=6000),
        }
        insights = [{"cols": ("X", "Y"), "type": "correlation",
                     "r": 0.75, "is_nonlinear": False, "text": "Fuerte"}]
        recs = recommender.recommend_charts(metadata, insights)
        types = [r["chart_type"] for r in recs]
        self.assertIn("density_heatmap", types)
        self.assertNotIn("scatter", types)

    def test_boxplot_priority_higher_than_bar_aggregation(self):
        """Segmented boxplots must rank before bar aggregations (fixes dynamite plot anti-pattern)."""
        metadata = {
            "Cat": self._base_meta("Nominal", 3),
            "Val": self._base_meta("Quantitative", 50),
        }
        insights = [{"cols": ("Cat", "Val"), "type": "aggregation",
                     "text": "Diferencia"}]
        recs = recommender.recommend_charts(metadata, insights)
        types = [r["chart_type"] for r in recs]
        self.assertIn("boxplot_segmented", types)
        self.assertIn("bar_aggregation", types)
        box_idx = types.index("boxplot_segmented")
        bar_idx = types.index("bar_aggregation")
        self.assertLess(box_idx, bar_idx,
                        "Boxplot (priority 75) must appear before bar_aggregation (priority 60)")

    def test_no_pie_chart_for_4_or_more_categories(self):
        """Pie charts must not appear for categorical columns with 4+ groups."""
        metadata = {"Producto": self._base_meta("Nominal", 5)}
        recs = recommender.recommend_charts(metadata, [])
        types = [r["chart_type"] for r in recs]
        self.assertNotIn("pie", types)
        self.assertIn("bar_frequency", types)

    def test_pie_chart_only_for_3_or_fewer_with_low_priority(self):
        """Pie charts are acceptable ONLY for <= 3 categories and must have priority <= 30."""
        metadata = {"Estado": self._base_meta("Nominal", 2)}
        recs = recommender.recommend_charts(metadata, [])
        pie_recs = [r for r in recs if r["chart_type"] == "pie"]
        if pie_recs:
            self.assertLessEqual(pie_recs[0]["priority"], 30)

    def test_high_cardinality_uses_horizontal_bar(self):
        """Nominal columns with > 12 categories must use horizontal bar charts."""
        metadata = {"Ciudad": self._base_meta("Nominal", 15)}
        recs = recommender.recommend_charts(metadata, [])
        types = [r["chart_type"] for r in recs]
        self.assertIn("bar_horizontal", types)
        self.assertNotIn("bar_frequency", types)

    def test_recommendations_sorted_by_priority_descending(self):
        """All recommendations must be sorted by priority in descending order."""
        metadata = {
            "Fecha":     {"type": "Temporal", "is_discrete": False,
                          "n_distinct": 50, "n_rows": 100, "insights": []},
            "Categoria": self._base_meta("Nominal", 4),
            "Ventas":    self._base_meta("Quantitative", 50),
            "Gastos":    self._base_meta("Quantitative", 50),
        }
        insights = [{"cols": ("Ventas", "Gastos"), "type": "correlation",
                     "r": 0.80, "is_nonlinear": False, "text": "Fuerte"}]
        recs = recommender.recommend_charts(metadata, insights)
        priorities = [r["priority"] for r in recs]
        self.assertEqual(priorities, sorted(priorities, reverse=True),
                         "Recommendations must be sorted in descending priority order")


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestSemanticTypeInference))
    suite.addTests(loader.loadTestsFromTestCase(TestBivariateInsights))
    suite.addTests(loader.loadTestsFromTestCase(TestChartRecommender))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
