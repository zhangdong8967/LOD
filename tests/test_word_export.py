"""Tests for manuscript Word export helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from lod_guide.paper.word_export import (
    build_chinese_markdown,
    build_combined_markdown,
    normalize_math_for_word,
    normalize_pandoc_superscripts,
    strip_body_bold_for_word,
    strip_internal_markdown_links,
)


def test_strip_internal_markdown_links():
    text = "See [SUPPLEMENT.md](SUPPLEMENT.md) and [OUP](https://oup.com/page)."
    out = strip_internal_markdown_links(text)
    assert "SUPPLEMENT.md" not in out or "](SUPPLEMENT" not in out
    assert "https://oup.com/page" in out


def test_normalize_math_for_word():
    text = r"(\(\operatorname{LoD}_{95}=1\), \(\operatorname{SE}(\log_{10}\operatorname{LoD})\))"
    out = normalize_math_for_word(text)
    assert "$LoD_{95}=1$" in out
    assert "$\\mathrm{SE}(\\log_{10} LoD)$" in out or "$\\mathrm{SE}(\\log_{10}LoD)$" in out


def test_strip_body_bold_for_word():
    text = "## Introduction\n\nNine deposits calibrate guidance **n** versus folklore.\n\n## Abstract\n\n**Background.** Many protocols fix **n**."
    out = strip_body_bold_for_word(text)
    assert "guidance n versus" in out
    assert "**Background.**" in out
    assert "Many protocols fix n." in out or "fix n." in out


def test_normalize_pandoc_superscripts():
    text = "**Authors:** MD^a,b · ^a Dept · \\(n^{\\ast}\\)"
    out = normalize_pandoc_superscripts(text)
    assert "MD^a,b^" in out
    assert "^a^ Dept" in out
    assert "\\(n^{\\ast}\\)" in out


def test_build_combined_markdown_author_superscripts():
    md = build_combined_markdown()
    assert "MD^a,b^" in md
    assert "^a^ Department" in md


def test_build_combined_markdown_main_text_only():
    md = build_combined_markdown()
    assert "# Figure legends" not in md
    assert "Fig. 1" in md or "Fig 1" in md
    assert "Fig. 2" in md or "Fig 2" in md
    assert "panel A" in md.lower() or "Panel A" in md or "panels A" in md


def test_build_figure_legends_markdown():
    from lod_guide.paper.word_export import build_figure_legends_markdown

    md = build_figure_legends_markdown()
    assert "# Figure legends" in md
    assert "Fig 1" in md
    assert "Fig 2" in md
    assert "Alt text" in md


def test_build_chinese_markdown():
    md = build_chinese_markdown()
    assert "临床检出限验证" in md
    assert "张东" in md
    assert "ORCID" not in md
    assert "**背景。**" in md
    assert "guidance **n**" not in md


def test_export_chinese_manuscript_docx(tmp_path: Path):
    from lod_guide.paper.word_export import export_chinese_manuscript_docx

    paths = export_chinese_manuscript_docx(out_dir=tmp_path)
    assert paths["chinese_docx"].exists()
    assert paths["chinese_docx"].stat().st_size > 5000


@pytest.mark.skipif(
    not __import__("shutil").which("pandoc"),
    reason="pandoc not installed",
)
def test_export_manuscript_docx(tmp_path: Path):
    from lod_guide.paper.word_export import export_manuscript_docx

    paths = export_manuscript_docx(out_dir=tmp_path)
    assert paths["submission_docx"].exists()
    assert paths["tables_docx"].exists()
    assert paths["legends_docx"].exists()
    assert paths["submission_docx"].stat().st_size > 5000
