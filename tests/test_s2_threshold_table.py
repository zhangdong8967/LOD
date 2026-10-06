"""S2 threshold table export."""

from __future__ import annotations

from lod_guide.research.s2_threshold_table import export_s2_threshold_table, s2_threshold_rows


def test_s2_threshold_rows_cover_domains():
    rows = s2_threshold_rows()
    domains = {r["Domain"] for r in rows}
    assert domains >= {"Shape", "Censoring", "Heterogeneity", "Gate"}
    assert len(rows) == 8


def test_export_s2_threshold_table(tmp_path):
    paths = export_s2_threshold_table(tmp_path)
    csv_path = tmp_path / "Table02a_s2_diagnostic_thresholds.csv"
    assert csv_path.exists()
    text = csv_path.read_text(encoding="utf-8")
    assert "parametric_candidate" in text
    assert "0.5" in text
    assert paths["csv"] == str(csv_path)
