"""
Clinical Chemistry Word handoff — combine manuscript markdown and export via pandoc.
"""

from __future__ import annotations

import csv
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANUSCRIPT = ROOT / "manuscript"
TABLE_DIR = ROOT / "paper_artifacts" / "tables" / "manuscript"
OUT_DIR = ROOT / "paper_artifacts" / "manuscript"

_BACKTICK_REPLACEMENTS: dict[str, str] = {
    "SUPPLEMENT.md": "online Supplement",
    "WORKED_EXAMPLE.md": "Supplement worked example",
    "COVER_LETTER.md": "cover letter",
    "CLINICAL_CHEMISTRY_SUBMISSION.md": "submission checklist",
    "FIGURE_LEGENDS_CC.md": "figure legends",
    "INTRODUCTION_FULL.md": "Introduction supplement",
    "METHODS_BRIEF.md": "manuscript",
    "make paper-artifacts": "archived build pipeline",
    "paper_artifacts/": "archived artifact bundle",
    "paper_artifacts/MANIFEST.json": "artifact manifest",
    "data/research/": "research data archive",
    "data/raw/evidence_manifest.json": "evidence manifest",
    "data/simulated/dgp_catalogue.json": "simulation catalogue",
    "lod_guide": "lod_guide",
    "Table03_comparison_grid_n20.csv": "Supplement Table 3 grid CSV",
    "minimax_probit_design.json": "Supplement design JSON",
    "c_optimal_lod_design.json": "Supplement design JSON",
    "pre_test_lob_inflation.json": "Supplement LoB JSON",
    "decision_risk.json": "Supplement decision-risk JSON",
}


def strip_internal_markdown_links(text: str) -> str:
    """Replace internal repo markdown links with plain text; keep external URLs."""

    def repl(m: re.Match[str]) -> str:
        label, url = m.group(1), m.group(2)
        if url.startswith(("http://", "https://", "mailto:")):
            return m.group(0)
        return label

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl, text)


def _replace_backtick_refs(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        raw = m.group(1)
        return _BACKTICK_REPLACEMENTS.get(raw, raw.split("/")[-1].replace("_", " "))

    return re.sub(r"`([^`]+)`", repl, text)


def normalize_math_for_word(text: str) -> str:
    """
    Pandoc + Word (--mathml) renders \\( ... \\) poorly; $ ... $ works.
    Simplify \\operatorname{LoD} etc. inside math for OMML compatibility.
    """
    # Display math blocks: normalize content only, keep delimiters.
    def fix_math_content(m: str) -> str:
        s = m
        for op in ("LoD", "SE", "expit", "logit"):
            s = s.replace(f"\\operatorname{{{op}}}", "LoD" if op == "LoD" else f"\\mathrm{{{op}}}")
        s = s.replace("\\operatorname{LoD}_{95}", "LoD_{95}")
        return s

    def display_repl(m: re.Match[str]) -> str:
        return f"\\[\n{fix_math_content(m.group(1))}\n\\]"

    text = re.sub(r"\\\[(.*?)\\\]", display_repl, text, flags=re.S)

    def inline_repl(m: re.Match[str]) -> str:
        return f"${fix_math_content(m.group(1))}$"

    text = re.sub(r"\\\((.*?)\\\)", inline_repl, text)
    return text


def strip_body_bold_for_word(text: str) -> str:
    """
    Clinical Chemistry body text should not use markdown emphasis bold.
    Keep bold only on title-page / abstract / ack field labels, not inline emphasis.
    """
    keep_label = re.compile(
        r"^\*\*(?:Title|Running title|Authors|Corresponding author|Affiliations|"
        r"Word count|Figures|Tables|Brief Summary|Keywords|Abbreviations|"
        r"Background\.|Methods\.|Results\.|Conclusions\.|"
        r"Funding:|Conflicts of interest:|Author contributions:|"
        r"Journal:|Compliance note:|Artificial intelligence disclosure\.|"
        r"Why this belongs|Relation to prior work\.|Evidence and scope|Availability\.|"
        r"Manuscript type:|Compliance:|Companion:|Main figures|Software:|Stance:|"
        r"题目|短标题|作者|通讯作者|作者单位|正文篇幅|图|表|简要说明|关键词|缩略语|"
        r"背景[\.。]|方法[\.。]|结果[\.。]|结论[\.。]|基金|利益冲突|作者贡献)"
    )
    imrad = re.compile(
        r"^(\*\*(?:Background\.|Methods\.|Results\.|Conclusions\.|"
        r"背景[\.。]|方法[\.。]|结果[\.。]|结论[\.。])\*\*)(.*)$"
    )
    field = re.compile(r"^(\*\*[^*]+(?:\*\*|\:\*\*))(.*)$")

    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        m = imrad.match(line)
        if m:
            lines.append(m.group(1) + re.sub(r"\*\*([^*]+)\*\*", r"\1", m.group(2)))
            continue
        if keep_label.match(stripped):
            m2 = field.match(line)
            if m2 and m2.group(2).strip():
                lines.append(m2.group(1) + re.sub(r"\*\*([^*]+)\*\*", r"\1", m2.group(2)))
            else:
                lines.append(line)
            continue
        lines.append(re.sub(r"\*\*([^*]+)\*\*", r"\1", line))
    return "\n".join(lines)


def normalize_pandoc_superscripts(text: str) -> str:
    """
    Pandoc markdown superscript requires closing carets: ^a,b^ not ^a,b.
    Fix author/affiliation markers for Word export without touching math blocks.
    """
    parts = re.split(r"(\$[^$]+\$|\\\([^)]*\\\))", text)
    for i in range(0, len(parts), 2):
        chunk = parts[i]
        chunk = re.sub(r"((?:MD|PhD))\^a,b(?!\^)", r"\1^a,b^", chunk)
        chunk = re.sub(r"(?<!\^)\^([ab])(?=[\s·(])", r"^\1^", chunk)
        parts[i] = chunk
    return "".join(parts)


def sanitize_manuscript_for_word(text: str) -> str:
    """Remove repo-only navigation and duplicate abstract fields for ScholarOne handoff."""
    text = strip_internal_markdown_links(text)
    text = _replace_backtick_refs(text)
    text = normalize_math_for_word(text)
    text = normalize_pandoc_superscripts(text)
    text = strip_body_bold_for_word(text)

    # Drop internal meta block between H1 title and title page content.
    text = re.sub(
        r"(^# .+\n)\n(?:\*\*Manuscript type:\*\*|\*\*Compliance:\*\*|\*\*Companion:\*\*"
        r"|\*\*Main figures|\*\*Software:\*\*|\*\*Stance:\*\*).+?\n---\n\n",
        r"\1\n\n",
        text,
        count=1,
        flags=re.S | re.M,
    )

    # Title page heading → plain start (CC first page has no section title).
    text = re.sub(
        r"## Title page \(Clinical Chemistry first page\)\n\n",
        "",
        text,
        count=1,
    )
    text = re.sub(
        r"## 标题页\n\n",
        "",
        text,
        count=1,
    )

    # Drop ORCID lines if present.
    text = re.sub(r"^\*\*ORCID:\*\*[^\n]+\n\n?", "", text, flags=re.M)

    # Remove duplicate Keywords block inside Abstract only.
    text = re.sub(
        r"(## Abstract\n.*?)(\n\*\*Keywords:\*\*[^\n]+\n)",
        r"\1",
        text,
        count=1,
        flags=re.S,
    )

    # Flatten Introduction subheadings to CC-style unnumbered sections.
    text = re.sub(r"^### ", "## ", text, flags=re.M)

    # Remove markdown horizontal rules (Pandoc renders them as lines in Word).
    text = re.sub(r"^\s*---\s*$", "", text, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Drop duplicate manuscript H1 (title page follows on first page).
    text = re.sub(r"^# [^\n]+\n\n", "", text, count=1, flags=re.M)

    # Remove reference-list generator footnote.
    text = re.sub(
        r"\n\*\(Generated by .*?EndNote files.*?\)\*\n?",
        "\n",
        text,
        flags=re.S,
    )

    text = _flatten_pipe_tables_for_submission(text)

    return text


def _flatten_pipe_tables_for_submission(text: str) -> str:
    """Convert remaining markdown pipe tables to bullets (ScholarOne main doc: no embedded tables)."""

    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\|\s*[-:]+", lines[i + 1].strip()):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2  # skip header + separator
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if len(cells) == len(header):
                    row = "; ".join(f"{h}: {c}" for h, c in zip(header, cells) if c)
                    out.append(f"- {row}")
                i += 1
            out.append("")
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def _read_manuscript_section(path: Path) -> str:
    return sanitize_manuscript_for_word(path.read_text(encoding="utf-8"))


def _round_cell(value: str, *, decimals: int = 3) -> str:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return value
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.{decimals}f}"


def csv_to_markdown_table(
    path: Path,
    *,
    columns: list[str] | None = None,
    headers: dict[str, str] | None = None,
    max_rows: int | None = None,
    round_floats: bool = True,
) -> str:
    """Render a CSV as a markdown table for pandoc → Word."""
    if not path.exists():
        return f"*[{path.name} not found]*\n"

    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return ""

    keys = columns or list(rows[0].keys())
    labels = [headers.get(k, k) if headers else k for k in keys]

    lines = [
        "| " + " | ".join(labels) + " |",
        "| " + " | ".join("---" for _ in keys) + " |",
    ]
    body = rows[:max_rows] if max_rows is not None else rows
    for row in body:
        cells = []
        for k in keys:
            val = row.get(k, "")
            if round_floats and val not in ("", None):
                val = _round_cell(val)
            cells.append(str(val))
        lines.append("| " + " | ".join(cells) + " |")

    if max_rows is not None and len(rows) > max_rows:
        lines.append(
            f"\n*… {len(rows) - max_rows} additional rows in online Supplement `{path.name}`.*"
        )
    return "\n".join(lines) + "\n"


_TIER_A_SHORT_LABELS: dict[str, str] = {
    "zenodo_mus_wt_qpcr": "Piaggio et al. (2024) Mus WT qPCR",
    "zenodo_mus_multiplex_qpcr": "Piaggio et al. (2024) multiplex qPCR",
    "analyseit_ep17_estradiol": "Analyse-it EP17 estradiol",
    "analyseit_ep17_probit": "Analyse-it EP17 probit/hit-rate",
    "mendeley_carobene_lombardy_eqa": "Carobene et al. (2026) Lombardy EQA",
    "bioc_msstats_lobd_cptac": "MSstatsLOBD / CPTAC proteomics",
    "zenodo_radioimmuno_precision": "Malkamäki et al. (2024) radioimmuno precision",
    "zenodo_radioimmuno_linearity": "Malkamäki et al. (2024) radioimmuno linearity",
    "zenodo_rmn_qualification": "Sawant et al. (2025) RMN qualification",
}


def _table7_markdown_for_word() -> str:
    """Render Table 7 from tier-A meta CSV (raw or manuscript-mapped schema)."""
    path = TABLE_DIR / "Table07_tierA_meta.csv"
    if not path.exists():
        return f"*[{path.name} not found]*\n"

    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return ""

    keys = [
        "No",
        "Source",
        "result_family",
        "model_path",
        "guidance_n",
        "folklore_n",
        "n_ratio_vs_folklore",
        "loq_at_cv20",
    ]
    labels = [
        "No.",
        "Source",
        "Result family",
        "Model path",
        "Guidance $n$",
        "Folklore $n$",
        "$n_{\\mathrm{guidance}}/n_{20}$",
        "LoQ@CV20%",
    ]
    lines = [
        "| " + " | ".join(labels) + " |",
        "| " + " | ".join("---" for _ in keys) + " |",
    ]
    for i, row in enumerate(rows, start=1):
        did = row.get("dataset_id") or row.get("Dataset_ID") or ""
        source = (
            row.get("Citation")
            or row.get("citation")
            or _TIER_A_SHORT_LABELS.get(did, did)
        )
        if len(str(source)) > 72:
            source = str(source)[:69] + "..."
        ratio = row.get("n_ratio_vs_folklore") or row.get("n_star_over_n20") or ""
        loq = row.get("loq_at_cv20") or ""
        cells = [
            str(i),
            str(source),
            str(row.get("result_family") or ""),
            str(row.get("model_path") or ""),
            _round_cell(row.get("guidance_n") or ""),
            _round_cell(row.get("folklore_n") or ""),
            _round_cell(ratio) if ratio not in ("", None) else "",
            _round_cell(loq) if loq not in ("", None) else "",
        ]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def build_main_tables_markdown() -> str:
    """Main-text Tables 1, 3, 7 for insertion after the reference list."""
    parts = ["\\newpage", "", "# Tables", ""]

    parts.extend(
        [
            "## Table 1. Detection claim structures mapped to sample-size methods",
            "",
            csv_to_markdown_table(
                TABLE_DIR / "Table01_estimands_E1_E3.csv",
                headers={
                    "Goal": "Goal",
                    "Estimand": "Statistical target",
                    "Definition": "Typical protocol language",
                    "Sample_size_method": "Sample-size method",
                },
            ),
            "",
            "\\newpage",
            "",
            "## Table 2. Two-arm operating characteristics: eight reference pairs at $n=20$ per arm",
            "",
            "*Full integer 50–99% comparison grid (1225 valid cells): online Supplement Table 3 CSV extension.*",
            "",
            csv_to_markdown_table(
                TABLE_DIR / "Table03_reference_pairs_n20.csv",
                columns=[
                    "pair",
                    "delta_p",
                    "n",
                    "power_exact_fisher",
                    "miss_beta",
                    "n_star_ceiling",
                ],
                headers={
                    "pair": "$(p_A,p_B)$",
                    "delta_p": "$\\Delta p$",
                    "n": "$n$/arm",
                    "power_exact_fisher": "Exact Fisher power",
                    "miss_beta": "Miss $\\beta$",
                    "n_star_ceiling": "$n^{\\ast}$ (80% power)",
                },
            ),
            "",
            "\\newpage",
            "",
            "## Table 3. Tier A public-deposit calibration meta-summary",
            "",
            "*One row per evidence-tier-A dataset ($n=10$): parametric gate outcome, model path, "
            "guidance $n$ versus folklore $n=20$, ratio $n_{\\mathrm{guidance}}/n_{20}$ when applicable, "
            "and LoQ@CV20% when a precision profile applies. Blank ratio cells indicate no comparable "
            "guidance path or missing contrast inputs (Fig. 2B labels these “ratio N/A”). "
            "Tier C/S deposits are excluded by design. Supports Fig. 2.*",
            "",
            _table7_markdown_for_word(),
            "",
        ]
    )
    return "\n".join(parts)


def build_chinese_markdown() -> str:
    """Standalone Chinese manuscript markdown (no figure legends)."""
    return _read_manuscript_section(MANUSCRIPT / "METHODS_BRIEF_ZH.md").rstrip() + "\n"


def build_main_text_markdown() -> str:
    """IMRAD through References only — no tables or figure legends."""
    return _read_manuscript_section(MANUSCRIPT / "METHODS_BRIEF.md").rstrip() + "\n"


def build_figure_legends_markdown() -> str:
    legends_raw = (MANUSCRIPT / "FIGURE_LEGENDS_CC.md").read_text(encoding="utf-8")
    body = "\n".join(legends_raw.splitlines()[4:]).strip()
    return "# Figure legends\n\n" + sanitize_manuscript_for_word(body) + "\n"


def build_combined_markdown(
    *,
    include_cover_letter: bool = False,
    include_tables: bool = False,
    include_legends: bool = False,
) -> str:
    """Assemble markdown for export; submission uses main text only."""
    parts: list[str] = [build_main_text_markdown().rstrip()]

    if include_tables:
        parts.extend(["", build_main_tables_markdown().rstrip()])

    if include_legends:
        parts.extend(["", "\\newpage", "", build_figure_legends_markdown().rstrip()])

    if include_cover_letter:
        letter = sanitize_manuscript_for_word(
            (MANUSCRIPT / "COVER_LETTER.md").read_text(encoding="utf-8"),
        )
        parts.extend(["", "\\newpage", "", letter.rstrip()])

    return "\n".join(parts) + "\n"


def _pandoc_to_docx(md_path: Path, docx_path: Path, *, title: str | None = None) -> None:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("pandoc not found — install with: brew install pandoc")
    cmd = [
        pandoc,
        str(md_path),
        "--from=markdown+tex_math_dollars",
        "--to=docx",
        "--mathml",
        f"--output={docx_path}",
        f"--resource-path={MANUSCRIPT}:{ROOT}",
    ]
    if title is not None:
        cmd.extend(["--metadata", f"title={title}"])
    subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
    )


def export_manuscript_docx(
    *,
    out_dir: Path | None = None,
    include_cover_letter: bool = False,
) -> dict[str, Path]:
    """
    Write separate ScholarOne handoff files under paper_artifacts/manuscript/.

    - Clinical_Chemistry_submission.docx — main text only (IMRAD + refs)
    - Tables_main.docx — Tables 1, 3, 7
    - Figure_legends.docx — figure legends + alt text
    - Clinical_Chemistry_author_bundle.docx — optional all-in-one for co-authors
    """
    out = out_dir or OUT_DIR
    out.mkdir(parents=True, exist_ok=True)

    main_md = out / "Clinical_Chemistry_main.md"
    tables_md = out / "Tables_main.md"
    legends_md = out / "Figure_legends.md"
    bundle_md = out / "Clinical_Chemistry_author_bundle.md"

    main_md.write_text(build_main_text_markdown(), encoding="utf-8")
    tables_md.write_text(build_main_tables_markdown(), encoding="utf-8")
    legends_md.write_text(build_figure_legends_markdown(), encoding="utf-8")
    bundle_md.write_text(
        build_combined_markdown(
            include_tables=True,
            include_legends=True,
            include_cover_letter=include_cover_letter,
        ),
        encoding="utf-8",
    )

    submission_docx = out / "Clinical_Chemistry_submission.docx"
    tables_docx = out / "Tables_main.docx"
    legends_docx = out / "Figure_legends.docx"
    bundle_docx = out / "Clinical_Chemistry_author_bundle.docx"
    combined_md = out / "Clinical_Chemistry_combined.md"

    title = "Prospective Sample-Size Planning for Limit-of-Detection Verification Under CLSI EP17"
    _pandoc_to_docx(main_md, submission_docx, title=None)
    _pandoc_to_docx(tables_md, tables_docx, title=f"{title} — Tables")
    _pandoc_to_docx(legends_md, legends_docx, title=f"{title} — Figure legends")
    _pandoc_to_docx(bundle_md, bundle_docx, title=f"{title} — Author bundle")

    combined_md.write_text(
        build_combined_markdown(include_tables=False, include_legends=False),
        encoding="utf-8",
    )

    return {
        "main_md": main_md,
        "tables_md": tables_md,
        "legends_md": legends_md,
        "combined_md": combined_md,
        "submission_docx": submission_docx,
        "tables_docx": tables_docx,
        "legends_docx": legends_docx,
        "author_bundle_docx": bundle_docx,
    }


def export_chinese_manuscript_docx(*, out_dir: Path | None = None) -> dict[str, Path]:
    """Standalone Chinese Word draft (internal / co-author review; not for CC upload)."""
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("pandoc not found — install with: brew install pandoc")

    out = out_dir or OUT_DIR
    out.mkdir(parents=True, exist_ok=True)

    zh_md = out / "LOD_manuscript_zh.md"
    zh_docx = out / "LOD_manuscript_zh.docx"

    zh_md.write_text(build_chinese_markdown(), encoding="utf-8")

    subprocess.run(
        [
            pandoc,
            str(zh_md),
            "--from=markdown+tex_math_dollars",
            "--to=docx",
            "--mathml",
            f"--output={zh_docx}",
            f"--resource-path={MANUSCRIPT}:{ROOT}",
            "--metadata",
            "lang=zh-CN",
            "--metadata",
            "title=临床检出限验证的前瞻性样本量设计",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return {"chinese_md": zh_md, "chinese_docx": zh_docx}


def export_cover_letter_docx(*, out_dir: Path | None = None) -> Path:
    """Standalone cover letter docx for ScholarOne upload."""
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("pandoc not found")

    out = out_dir or OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    letter_md = out / "Cover_letter.md"
    letter_docx = out / "Cover_letter.docx"
    letter_md.write_text(
        sanitize_manuscript_for_word(
            (MANUSCRIPT / "COVER_LETTER.md").read_text(encoding="utf-8"),
        ),
        encoding="utf-8",
    )
    subprocess.run(
        [pandoc, str(letter_md), "--from=markdown+tex_math_dollars", "--to=docx", "--mathml", f"--output={letter_docx}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return letter_docx
