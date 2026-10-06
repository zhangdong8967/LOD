#!/usr/bin/env python3
"""
Assemble final Clinical Chemistry submission bundle under manuscript/.

Uses the root Clinical_Chemistry_submission.docx (intact Word math) as the main
manuscript base, revised M/R/D text files, and figure/table sections extracted
from Clinical_Chemistry_author_bundle.docx (math preserved).

Never assigns para.text on paragraphs that contain OMML math — that destroys
equations.  Plain-text patches use w:t nodes outside m:oMath only.
"""

from __future__ import annotations

import re
import shutil
import zipfile
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
SUBMISSION_SRC = ROOT / "submission"
MANUSCRIPT = ROOT / "manuscript"

# Root copy retains Brief Summary / Abbreviations math objects.
MAIN_SRC = ROOT / "Clinical_Chemistry_submission.docx"
AUTHOR_BUNDLE = SUBMISSION_SRC / "Clinical_Chemistry_author_bundle.docx"

METHODS_TXT = SUBMISSION_SRC / "METHODS_FINAL_FOR_MANUSCRIPT.docx.txt"
RESULTS_TXT = SUBMISSION_SRC / "RESULTS_REVISED_NATURAL.txt"
DISCUSSION_TXT = SUBMISSION_SRC / "DISCUSSION_REVISED_NATURAL.txt"
INTRODUCTION_TXT = SUBMISSION_SRC / "INTRODUCTION_REVISED_NATURAL.txt"
EQ2_SNIPPET_PATH = SUBMISSION_SRC / "assets" / "methods_equation2_snippets.xml"
REFERENCES_TXT = SUBMISSION_SRC / "REFERENCES_FINAL_29.txt"
ABSTRACT_BRIEF_TXT = SUBMISSION_SRC / "ABSTRACT_BRIEF_SUMMARY.txt"
COVER_LETTER_TXT = SUBMISSION_SRC / "COVER_LETTER_FINAL.txt"
MANUSCRIPT_TITLE = (
    "Claim-specific sample-size planning for binary hit-rate LoD verification"
)
TITLE_XML_SNIPPET_OLD = (
    '<w:t>A</w:t></w:r><w:r w:rsidR="0063093F"><w:rPr><w:rStyle w:val="Strong"/></w:rPr>'
    '<w:t xml:space="preserve"> statistical framework for claim-specific verification of '
    "low-end analytical performance in clinical laboratory practice</w:t>"
)
TITLE_XML_SNIPPET_NEW = (
    '<w:t xml:space="preserve">Claim-specific sample-size planning for binary hit-rate '
    "LoD verification</w:t>"
)

_PARA_RE = re.compile(r"<w:p[ >].*?</w:p>", re.DOTALL)

METHODS_SUBHEADINGS = {
    "Study Design and Definition of Detection Claims",
    "Sample Size Planning and Exact Operating Characteristics",
    "Retrospective Audit of Validation Records",
    "Public Data Sources and Reproducibility",
}

RESULTS_SUBHEADINGS = {
    "Exact operating characteristics across the detection-probability lattice",
    "Two-arm lot comparison at the limit of detection",
    "Fixed pass criteria and observed positivity",
    "Benchmark confirmation of detection probability",
    "Worked example from an archived protocol sentence",
    "Retrospective audit of validation records",
    "Tier A protocol-file audit",
    "Hospital and published validation records",
}

TABLE1_GOAL_MAP = {
    "E1": "Benchmark confirmation",
    "E2": "Two-arm comparison",
    "E3": "Qualitative pass criteria",
}

LEGACY_TABLE_PHRASES: list[tuple[str, str]] = [
    (
        "Table 3. E2 operating characteristics: eight reference pairs",
        "Table 2. Two-arm operating characteristics: eight reference pairs",
    ),
    (
        "Table 7. Tier A public-deposit calibration meta-summary",
        "Table 3. Tier A public-deposit calibration meta-summary",
    ),
    (
        "tier A public deposits (Table 7)",
        "tier A public deposits (Table 3)",
    ),
    (
        "deposit labels match Table 7 abbreviations",
        "deposit labels match Table 3 abbreviations",
    ),
    ("(see Table 7)", "(see Table 3)"),
    (
        "Eight reference pairs marked (Table 3)",
        "Eight reference pairs marked (Table 2)",
    ),
    (
        "reference E2 probability pairs (Table 3)",
        "reference protocol-specific probability pairs (Table 2)",
    ),
    (
        "audited archived validation language in ten tier A public files (Table 7)",
        "audited archived validation language in ten tier A public files (Table 3)",
    ),
    (
        "Protocol-file audit on Table 7 and Supplementary Table 7b",
        "Protocol-file audit on Table 3 and Supplementary Table 7b",
    ),
    (
        "ratios versus conventional 20 often 2.6×–10× (Fig. 2; Table 7)",
        "ratios versus conventional 20 often 2.6×–10× (Fig. 2; Table 3)",
    ),
    (
        "Table 3 holds eight protocol-specific pairs",
        "Table 2 holds eight protocol-specific pairs",
    ),
    (
        "(Results; Fig. 1B–C; Table 3)",
        "(Results; Fig. 1B–C; Table 2)",
    ),
    (
        "(Fig 1B–C; Table 3; Supplementary Table 3f)",
        "(Fig 1B–C; Table 2; Supplementary Table 3f)",
    ),
    (
        "(Fig. 1B–C; Table 3; Supplementary Table 3f)",
        "(Fig. 1B–C; Table 2; Supplementary Table 3f)",
    ),
    (
        "comparison pairs (median ; Table 3)",
        "comparison pairs (median 3.9×; Table 2)",
    ),
    (
        "Table 1. Detection claims E1–E3 mapped to sample-size engines",
        "Table 1. Detection claim structures mapped to sample-size methods",
    ),
    ("distinct from E1 confirmation", "distinct from benchmark confirmation"),
    ("A. E2 planning framework", "A. Two-arm planning framework"),
    ("lattice-based E2 planning surfaces", "lattice-based two-arm planning surfaces"),
    (
        "EP17 estradiol E1 versus E3 rule",
        "EP17 estradiol benchmark confirmation versus qualitative pass rule",
    ),
    ("reference E2 pairs", "reference protocol-specific pairs"),
    (
        "61% of cells have β>0.8.",
        "61% of cells have β>0.8 (a property of the equally spaced design lattice, not a laboratory prevalence).",
    ),
    (
        '0.8</m:t></m:r></m:oMath><w:r><w:t xml:space="preserve">. Eight reference pairs marked',
        '0.8</m:t></m:r></m:oMath><w:r><w:t xml:space="preserve"> (a property of the equally spaced design lattice, not a laboratory prevalence). Eight reference pairs marked',
    ),
    (
        "median Lconventional/Lpowered=3.9; Table 3",
        "median Lconventional/Lpowered=3.9; Table 2",
    ),
    ("versus folklore", "versus conventional"),
    ('xml:space="preserve">Folklore</w:t>', 'xml:space="preserve">Conventional</w:t>'),
    (">Folklore</w:t>", ">Conventional</w:t>"),
    (
        "Two-arm planning framework on the integer",
        "Three-step planning banner (lock the claim, score n=20, plan n* as a function of delta p); heatmaps use the integer",
    ),
    (". Inset: median", ". Marginal by contrast, median"),
    (
        "Panel A: lattice-based two-arm planning surfaces over hit rates 50 through 99 percent.",
        "Panel A: lock the claim, score n=20 on the design lattice, then plan n-star as a function of delta p.",
    ),
    (
        "Panel C: log-scale design surface n star with inset median n star versus delta p.",
        "Panel C: log-scale design surface n star; 90/80 pair marked.",
    ),
]

ABBREVIATIONS_OLD = (
    "E1, benchmark confirmation (detection claim); E2, two-arm contrast (detection claim); "
    "E3, fixed pass-rule (detection claim) (E1–E3 are Article labels in Table 1, not CLSI nomenclature);"
)
ABBREVIATIONS_NEW = (
    "benchmark confirmation, two-arm comparison, and qualitative pass criteria "
    "(detection-claim types in Table 1, not CLSI nomenclature);"
)

# Plain-text fixes for cover letters whose math objects were previously destroyed.
COVER_MATH_FIXES: list[tuple[str, str]] = [
    ("at  per arm, 61% of cells have miss probability  ", "at n=20 per arm, 61% of cells have miss probability β>0.8 "),
    ("folklore  per arm leaves miss probability  above", "conventional n=20 per arm leaves miss probability β>0.8 above"),
    ("folklore per arm leaves miss probability above", "conventional n=20 per arm leaves miss probability β>0.8 above"),
    ("illustrates a powered contrast ()", "illustrates a powered contrast (n*≈199)"),
    ("claim-versus- tension", "claim-versus-n tension"),
    ("Fig 1.", "Fig. 1."),
    ("Fig 2.", "Fig. 2."),
    ("Fig 2;", "Fig. 2;"),
    (
        "Prospective Sample Size Planning for Limit of Detection Verification Under CLSI EP17",
        MANUSCRIPT_TITLE,
    ),
    (
        "A statistical framework for claim-specific verification of low-end analytical performance in clinical laboratory practice",
        MANUSCRIPT_TITLE,
    ),
]


def load_section_paragraphs(path: Path, section_name: str) -> list[str]:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == section_name:
            start = i + 1
            break
    if start is None:
        raise ValueError(f"Section {section_name!r} not found in {path}")

    out: list[str] = []
    for line in lines[start:]:
        if line.startswith("====") or line.startswith("主要修改"):
            break
        if not line.strip():
            continue
        out.append(line.rstrip())
    return out


def find_paragraph_index(doc: Document, exact: str) -> int | None:
    for i, para in enumerate(doc.paragraphs):
        if para.text.strip() == exact:
            return i
    return None


def _paragraph_plain_text(para_xml: str) -> str:
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", para_xml)).strip()


def _escape_xml_text(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _paragraph_xml(text: str, style: str) -> str:
    return (
        f'<w:p><w:pPr><w:pStyle w:val="{style}"/><w:contextualSpacing/></w:pPr>'
        f'<w:r><w:t xml:space="preserve">{_escape_xml_text(text)}</w:t></w:r></w:p>'
    )


def _extract_methods_equation_omml(src: Path) -> dict[str, str]:
    """Pull display-equation OMML paragraphs for Eq. (2) from the base manuscript."""
    if EQ2_SNIPPET_PATH.exists():
        raw = EQ2_SNIPPET_PATH.read_text(encoding="utf-8")
        snippets: dict[str, str] = {}
        for part in raw.split("<!-- eq:"):
            if not part.strip():
                continue
            name, _, body = part.partition("-->")
            snippets[name.strip()] = body.strip()
        if snippets:
            return snippets

    xml = zipfile.ZipFile(src).read("word/document.xml").decode("utf-8")
    snippets = {}
    for para in _PARA_RE.findall(xml):
        if "<m:oMathPara>" not in para:
            continue
        plain = re.sub(r"<[^>]+>", "", para)
        if "napprox" in plain or "napprox" in plain.lower():
            snippets["eq_main"] = para
        elif len(plain.strip()) < 24 and ("p=" in plain or "p̄" in plain):
            snippets["eq_where"] = para

    if snippets:
        EQ2_SNIPPET_PATH.parent.mkdir(parents=True, exist_ok=True)
        blob = "".join(f"<!-- eq:{key} -->\n{value}\n" for key, value in snippets.items())
        EQ2_SNIPPET_PATH.write_text(blob, encoding="utf-8")
    return snippets


def _lines_to_paragraph_xml(
    section: str,
    lines: list[str],
    *,
    omml: dict[str, str] | None = None,
) -> list[str]:
    out: list[str] = []
    for text in lines:
        if section == "Methods" and omml:
            stripped = text.strip()
            if stripped.startswith("n* =") and "eq_main" in omml:
                out.append(omml["eq_main"])
                continue
            # Bare definition line for p-bar (keep surrounding "where" / prose as text).
            if (
                "eq_where" in omml
                and "(p_A+p_B)/2" in stripped.replace(" ", "")
                and len(stripped) <= 40
                and not stripped.lower().startswith("where")
            ):
                out.append(omml["eq_where"])
                continue
            # Legacy one-line form: "where p̄=... Rest of paragraph."
            if stripped.lower().startswith("where p") and "eq_where" in omml:
                out.append(_paragraph_xml("where", "NormalWeb"))
                out.append(omml["eq_where"])
                rest = re.sub(
                    r"^where\s+.*=\s*\(p_A\+p_B\)/2\.\s*",
                    "",
                    stripped,
                    flags=re.IGNORECASE,
                )
                if rest and rest != stripped:
                    out.append(_paragraph_xml(rest, "NormalWeb"))
                continue
        if section == "Methods" and text in METHODS_SUBHEADINGS:
            style = "NormalWeb"
        elif section in {"Results", "Discussion"} and (
            text in RESULTS_SUBHEADINGS or text == "Limitations"
        ):
            style = "Heading3"
        else:
            style = "NormalWeb"
        out.append(_paragraph_xml(text, style))
    return out


def _replace_xml_section(
    xml: str,
    section_title: str,
    next_section_title: str,
    lines: list[str],
    *,
    omml: dict[str, str] | None = None,
) -> str:
    paras = _PARA_RE.findall(xml)
    start_i = end_i = None
    for i, p in enumerate(paras):
        if _paragraph_plain_text(p) == section_title:
            start_i = i
        elif start_i is not None and _paragraph_plain_text(p) == next_section_title:
            end_i = i
            break
    if start_i is None or end_i is None:
        raise ValueError(f"Could not locate {section_title} → {next_section_title} in XML")

    new_paras = _lines_to_paragraph_xml(
        section_title,
        lines,
        omml=omml if section_title == "Methods" else None,
    )
    old_block = "".join(paras[start_i + 1 : end_i])
    new_block = "".join(new_paras)
    if old_block not in xml:
        raise ValueError(f"Could not splice section body for {section_title}")
    return xml.replace(old_block, new_block, 1)


def _xml_replacement_list(*, table_phrases: bool, abbreviations: bool, cover_fixes: bool) -> list[tuple[str, str]]:
    reps: list[tuple[str, str]] = []
    if table_phrases:
        reps.extend(LEGACY_TABLE_PHRASES)
        reps.append(("Supplement Table 7b", "Supplementary Table 7b"))
        reps.append(("Supplement Table", "Supplementary Table"))
    if abbreviations:
        reps.append((ABBREVIATIONS_OLD, ABBREVIATIONS_NEW))
    if cover_fixes:
        reps.extend(COVER_MATH_FIXES)
    reps.extend(
        [
            (
                "Fig 1. Prospective LoD protocol and E2 replicate planning",
                "Fig. 1. Prospective LoD protocol and two-arm replicate planning",
            ),
            ("Fig 2.", "Fig. 2."),
            ("E2 replicate planning", "two-arm replicate planning"),
        ]
    )
    return reps


def patch_docx_xml(doc_path: Path, *, table_phrases: bool = True, abbreviations: bool = False, cover_fixes: bool = False) -> int:
    """
    Apply literal string replacements to document.xml.

    Does not parse/re-serialize the XML tree (that strips OMML).  Uses only
    long, distinctive phrases so Supplementary Table labels stay safe.
    """
    replacements = _xml_replacement_list(
        table_phrases=table_phrases,
        abbreviations=abbreviations,
        cover_fixes=cover_fixes,
    )
    with zipfile.ZipFile(doc_path, "r") as zin:
        xml = zin.read("word/document.xml").decode("utf-8")
        names = zin.namelist()
        other = {n: zin.read(n) for n in names if n != "word/document.xml"}

    changed = 0
    for old, new in replacements:
        if old in xml:
            xml = xml.replace(old, new)
            changed += 1

    with zipfile.ZipFile(doc_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name in names:
            payload = xml.encode("utf-8") if name == "word/document.xml" else other[name]
            zout.writestr(name, payload)
    return changed


def _body_children_between(
    doc: Document,
    start_heading: str,
    end_heading: str | None,
) -> list:
    """Return body child elements from start_heading up to (not including) end_heading."""
    start_el = end_el = None
    for para in doc.paragraphs:
        text = para.text.strip()
        if text == start_heading:
            start_el = para._element
        elif end_heading and text == end_heading and start_el is not None:
            end_el = para._element
            break
    if start_el is None:
        raise ValueError(f"Heading not found: {start_heading}")

    body_children = list(doc.element.body)
    start_i = body_children.index(start_el)
    end_i = body_children.index(end_el) if end_el is not None else len(body_children)
    return body_children[start_i:end_i]


def extract_bundle_section(
    bundle_path: Path,
    start_heading: str,
    end_heading: str | None,
    dst_path: Path,
    title: str,
) -> None:
    """Copy a heading-bounded body range (paragraphs + tables) into a new docx."""
    src = Document(bundle_path)
    chunk = _body_children_between(src, start_heading, end_heading)

    dst = Document()
    for child in list(dst.element.body):
        dst.element.body.remove(child)

    for element in chunk:
        dst.element.body.append(deepcopy(element))

    dst.core_properties.title = title
    dst.save(dst_path)


def load_reference_lines(path: Path) -> list[str]:
    lines: list[str] = []
    started = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\d+\.\s", line.strip()):
            started = True
            lines.append(line.strip())
        elif started and line.startswith("===="):
            break
    return lines


def load_abstract_brief(path: Path) -> tuple[list[str], str]:
    raw = path.read_text(encoding="utf-8")
    abs_m = re.search(r"^ABSTRACT\n(.+?)(?=\nBRIEF_SUMMARY\n)", raw, re.S | re.M)
    brief_m = re.search(r"^BRIEF_SUMMARY\n(.+?)(?=\n====|\Z)", raw, re.S | re.M)
    if not abs_m or not brief_m:
        raise ValueError(f"Could not parse abstract/brief from {path}")
    abstract_paras = [ln.strip() for ln in abs_m.group(1).splitlines() if ln.strip()]
    brief = " ".join(brief_m.group(1).split())
    return abstract_paras, brief


def _replace_xml_tail_from_heading(xml: str, heading: str, lines: list[str], style: str = "Normal") -> str:
    """Replace all paragraphs after a heading through document end (before sectPr)."""
    paras = _PARA_RE.findall(xml)
    start_i = None
    for i, p in enumerate(paras):
        if _paragraph_plain_text(p) == heading:
            start_i = i
            break
    if start_i is None:
        raise ValueError(f"Heading not found for tail replace: {heading}")

    # Drop trailing empty paragraphs from the old block for a cleaner splice.
    end_i = len(paras)
    while end_i > start_i + 1 and not _paragraph_plain_text(paras[end_i - 1]):
        end_i -= 1

    new_paras = [_paragraph_xml(line, style) for line in lines]
    old_block = "".join(paras[start_i + 1 : end_i])
    new_block = "".join(new_paras)
    if old_block and old_block not in xml:
        raise ValueError(f"Could not splice tail after {heading}")
    if not old_block:
        # Insert before closing body / after heading para.
        heading_xml = paras[start_i]
        return xml.replace(heading_xml, heading_xml + new_block, 1)
    return xml.replace(old_block, new_block, 1)


def _count_main_text_words(xml: str) -> int:
    text = re.sub(r"</w:p>", "\n", xml)
    text = re.sub(r"<[^>]+>", "", text)
    start = text.find("\nIntroduction\n")
    end = text.find("\nData and code availability\n")
    if start < 0 or end < 0:
        return 0
    return len(re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?", text[start:end]))


def build_main_manuscript(src: Path, dst: Path) -> None:
    shutil.copy2(src, dst)
    omml = _extract_methods_equation_omml(src)
    with zipfile.ZipFile(dst, "r") as zin:
        xml = zin.read("word/document.xml").decode("utf-8")
        names = zin.namelist()
        other = {n: zin.read(n) for n in names if n != "word/document.xml"}

    if INTRODUCTION_TXT.exists():
        xml = _replace_xml_section(
            xml,
            "Introduction",
            "Methods",
            load_section_paragraphs(INTRODUCTION_TXT, "Introduction"),
        )

    xml = _replace_xml_section(
        xml,
        "Methods",
        "Results",
        load_section_paragraphs(METHODS_TXT, "Methods"),
        omml=omml,
    )
    xml = _replace_xml_section(
        xml, "Results", "Discussion", load_section_paragraphs(RESULTS_TXT, "Results")
    )
    xml = _replace_xml_section(
        xml,
        "Discussion",
        "Data and code availability",
        load_section_paragraphs(DISCUSSION_TXT, "Discussion"),
    )

    if REFERENCES_TXT.exists():
        xml = _replace_xml_tail_from_heading(
            xml, "References", load_reference_lines(REFERENCES_TXT), style="Normal"
        )

    if ABSTRACT_BRIEF_TXT.exists():
        abstract_paras, brief = load_abstract_brief(ABSTRACT_BRIEF_TXT)
        xml = _replace_xml_section(xml, "Abstract", "Introduction", abstract_paras)
        # Replace Brief Summary body while keeping the label prefix if present.
        brief_full = f"Brief Summary (≤100 words). {brief}"
        # Match existing brief paragraph text content via unique prefix.
        plain = re.sub(r"<[^>]+>", "", xml)
        old_brief_m = re.search(
            r"Brief Summary \(≤100 words\)\.\s*.+?(?=Keywords:)",
            plain,
            re.S,
        )
        if old_brief_m:
            # Replace within corresponding w:t nodes is fragile; replace full
            # distinctive opening sentence shared by old brief.
            old_open = "Signed LoD packets often freeze about 20 replicates"
            if old_open in xml:
                # Rebuild entire brief paragraph string in XML by replacing from
                # label through the end of the known brief paragraph.
                paras = _PARA_RE.findall(xml)
                for p in paras:
                    if "Brief Summary" in p and "Signed LoD packets" in p:
                        new_p = _paragraph_xml(brief_full, "NormalWeb")
                        xml = xml.replace(p, new_p, 1)
                        break

    for old, new in [
        (ABBREVIATIONS_OLD, ABBREVIATIONS_NEW),
        ("Supplement Table 7b", "Supplementary Table 7b"),
        ("Python $$3.10", "Python 3.10"),
        (
            "A statistical framework for claim-specific verification of low-end analytical performance in clinical laboratory practice",
            MANUSCRIPT_TITLE,
        ),
    ]:
        xml = xml.replace(old, new)
    if TITLE_XML_SNIPPET_OLD in xml:
        xml = xml.replace(TITLE_XML_SNIPPET_OLD, TITLE_XML_SNIPPET_NEW, 1)

    # Update title-page word count after content replacement.
    wc = _count_main_text_words(xml)
    if wc:
        xml = re.sub(r"~2,720", f"~{wc:,}", xml)
        xml = re.sub(r"~4,\d{3}", f"~{wc:,}", xml)

    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name in names:
            payload = xml.encode("utf-8") if name == "word/document.xml" else other[name]
            zout.writestr(name, payload)


def build_tables_from_bundle(bundle: Path, dst: Path) -> None:
    extract_bundle_section(
        bundle,
        "Tables",
        "Figure legends",
        dst,
        "Main tables",
    )
    patch_docx_xml(dst, table_phrases=True)

    # Table 1 goal-column labels (plain cells only).
    doc = Document(dst)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip() in TABLE1_GOAL_MAP:
                    cell.text = TABLE1_GOAL_MAP[cell.text.strip()]
    doc.save(dst)


def build_figure_legends_from_bundle(bundle: Path, dst: Path) -> None:
    extract_bundle_section(
        bundle,
        "Figure legends",
        None,
        dst,
        "Figure legends",
    )
    patch_docx_xml(dst, table_phrases=True)


def _load_cover_letter_paragraphs(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    start = 0
    for i, line in enumerate(lines):
        if line.startswith("Journal:"):
            start = i
            break
    out: list[str] = []
    for line in lines[start:]:
        if line.startswith("===="):
            break
        if not line.strip():
            continue
        out.append(line.rstrip())
    if not out:
        raise ValueError(f"No cover-letter body found in {path}")
    return out


def build_cover_letter(src: Path, dst: Path) -> None:
    """
    Rebuild cover letter from COVER_LETTER_FINAL.txt.

    The legacy Cover_letter.docx had Journal/Title/Authors jammed into one
    paragraph and destroyed OMML→plain gaps; regenerating avoids those defects.
    `src` is retained only as a fallback if the txt source is missing.
    """
    if COVER_LETTER_TXT.exists():
        paragraphs = _load_cover_letter_paragraphs(COVER_LETTER_TXT)
        doc = Document()
        for text in paragraphs:
            doc.add_paragraph(text)
        doc.core_properties.title = "Cover letter — Clinical Chemistry"
        doc.save(dst)
        return
    shutil.copy2(src, dst)
    patch_docx_xml(dst, table_phrases=True, cover_fixes=True)


def patch_online_supplement_pdf(src: Path, dst: Path) -> None:
    """
    Patch outdated front-matter / main-table references in Online_Supplement.pdf.

    Full rebuild needs manuscript/SUPPLEMENT.md + paper_artifacts tables (not in
    the current submission tree). Rewrites the page-1 header band and patches a
    few body phrases that still point at legacy main-text Table 7.
    """
    import fitz  # PyMuPDF

    doc = fitz.open(src)
    page0 = doc[0]
    top = page0.search_for("Online Supplement")[0]
    toc = page0.search_for("Table of contents")[0]
    header_rect = fitz.Rect(72, top.y0, page0.rect.width - 72, toc.y0 - 10)
    page0.add_redact_annot(header_rect, fill=(1, 1, 1))
    page0.apply_redactions()
    header = (
        "Online Supplement\n"
        f"Title: {MANUSCRIPT_TITLE}\n"
        "Companion: main manuscript (clinical planning in main text; "
        "formal verification logic and certificates here)\n"
        "Main manuscript figures/tables: Fig. 1 (A-D), Fig. 2 (A-C); Tables 1-3\n"
        "Theory layer (same submission): S2b (defects D1-D3) + S2e (formal theorems T1-T5; "
        "Proposition P23 allocation) + Table 4 (P1-P18 certificates)\n"
        "No supplement figures - tier A calibration is main Fig. 2; "
        "full two-arm grid is tabular/CSV.\n"
        "Numbering note. Supplement sections S1-S8 index tables and theory material, "
        "independent of the main-text planning pipeline S0-S7. "
        "Main-text tables are Tables 1-3 (the audit meta-summary formerly labeled Table 7 "
        "in older supplement prose is main-text Table 3).\n"
        "Rebuild artifacts: make paper-artifacts · Export this supplement: make supplement-pdf\n"
    )
    page0.insert_textbox(
        header_rect,
        header,
        fontsize=9,
        fontname="helv",
        color=(0, 0, 0),
        align=0,
    )

    body_reps = [
        ("Fig. 2 / Table 7 use tier A", "Fig. 2 / Table 3 use tier A"),
        ("Table 7 lists ten", "Table 3 lists ten"),
        ("row in Table 7", "row in Table 3"),
        ("Table 7 meta)", "Table 3 meta)"),
    ]
    for page in doc:
        hits: list[tuple[fitz.Rect, str]] = []
        for old, new in body_reps:
            for rect in page.search_for(old):
                box = fitz.Rect(rect.x0, rect.y0 - 0.5, rect.x1 + 12, rect.y1 + 0.5)
                hits.append((box, new))
                page.add_redact_annot(box, fill=(1, 1, 1))
        if not hits:
            continue
        page.apply_redactions()
        for box, new in hits:
            page.insert_text(
                (box.x0, box.y1 - 1.5),
                new,
                fontsize=9,
                fontname="helv",
                color=(0, 0, 0),
            )

    tmp = dst.with_suffix(".patched.pdf")
    doc.save(tmp, garbage=4, deflate=True)
    doc.close()
    tmp.replace(dst)


def build_author_bundle(
    main_path: Path,
    tables_path: Path,
    legends_path: Path,
    dst: Path,
) -> None:
    """Concatenate main manuscript + tables + figure legends for co-author review."""
    shutil.copy2(main_path, dst)
    main = Document(dst)
    tables = Document(tables_path)
    legends = Document(legends_path)

    # Page break before tables
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn as _qn

    break_p = main.add_paragraph()
    break_run = break_p.add_run()
    br = OxmlElement("w:br")
    br.set(_qn("w:type"), "page")
    break_run._element.append(br)

    for child in list(tables.element.body):
        # Skip sectPr trailers
        if child.tag.endswith("}sectPr"):
            continue
        main.element.body.append(deepcopy(child))

    break_p2 = main.add_paragraph()
    break_run2 = break_p2.add_run()
    br2 = OxmlElement("w:br")
    br2.set(_qn("w:type"), "page")
    break_run2._element.append(br2)

    for child in list(legends.element.body):
        if child.tag.endswith("}sectPr"):
            continue
        main.element.body.append(deepcopy(child))

    main.core_properties.title = (
        "Prospective Sample-Size Planning for LoD Verification — Author Bundle"
    )
    main.save(dst)


def copy_figures(fig_dir: Path) -> list[str]:
    fig_dir.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for name in [
        "Fig1_lod_replicate_planning.tif",
        "Fig1_lod_replicate_planning.png",
        "Fig2_tierA_calibration.tif",
        "Fig2_tierA_calibration.png",
    ]:
        src = SUBMISSION_SRC / name
        if src.exists():
            shutil.copy2(src, fig_dir / name)
            copied.append(name)
    return copied


def count_math(path: Path) -> int:
    with zipfile.ZipFile(path) as zf:
        return zf.read("word/document.xml").decode("utf-8").count("<m:oMath")


def verify_docx(path: Path) -> dict[str, int]:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8")
    plain = re.sub(r"<[^>]+>", " ", xml)
    plain = re.sub(r"\s+", " ", plain)
    return {
        "math_blocks": xml.count("<m:oMath"),
        "main_table_7": len(re.findall(r"(?<!Supplementary )Table 7\b", plain)),
        "main_table_3": len(re.findall(r"(?<!Supplementary )Table 3\b", plain)),
        "table_2": len(re.findall(r"\bTable 2\b", plain)),
        "e1_label": len(re.findall(r"\bE1\b", plain)),
        "e2_label": len(re.findall(r"\bE2\b", plain)),
        "e3_label": len(re.findall(r"\bE3\b", plain)),
        "broken_at_per_arm": plain.count("at  per arm"),
    }


def write_manifest() -> None:
    (MANUSCRIPT / "README.md").write_text(
        """# Clinical Chemistry submission bundle

Generated by `scripts/assemble_manuscript_submission.py`.

## Sources

- **Main manuscript**: `Clinical_Chemistry_submission.docx` (root; title-page math preserved)
  + revised Introduction / Methods / Results / Discussion from `submission/*.txt`
  + Methods Eq. (2) OMML snippets from base doc (`submission/assets/methods_equation2_snippets.xml`)
- **Tables & figure legends**: extracted from `submission/Clinical_Chemistry_author_bundle.docx`
  (OMML math preserved; table numbers patched in plain text only)
- **Cover letter**: rebuilt from `submission/COVER_LETTER_FINAL.txt`
- **Online Supplement**: `submission/Online_Supplement.pdf` with front-matter / Table 7→3 patches

## ScholarOne upload

| File | Role |
|------|------|
| `Cover_letter.docx` | Cover letter |
| `Clinical_Chemistry_submission.docx` | Main text |
| `figures/Fig1_lod_replicate_planning.tif` | Figure 1 |
| `figures/Fig2_tierA_calibration.tif` | Figure 2 |
| `Figure_legends.docx` | Legends |
| `Tables_main.docx` | Tables 1–3 |
| `Online_Supplement.pdf` | Supplement |
| `Clinical_Chemistry_author_bundle.docx` | Co-author review (main + tables + legends) |

## Regenerate

```bash
python scripts/assemble_manuscript_submission.py
```
""",
        encoding="utf-8",
    )


def main() -> None:
    if not MAIN_SRC.exists():
        raise SystemExit(f"Missing base manuscript: {MAIN_SRC}")
    if not AUTHOR_BUNDLE.exists():
        raise SystemExit(f"Missing author bundle: {AUTHOR_BUNDLE}")

    MANUSCRIPT.mkdir(parents=True, exist_ok=True)
    fig_dir = MANUSCRIPT / "figures"

    build_main_manuscript(MAIN_SRC, MANUSCRIPT / "Clinical_Chemistry_submission.docx")
    build_tables_from_bundle(AUTHOR_BUNDLE, MANUSCRIPT / "Tables_main.docx")
    build_figure_legends_from_bundle(AUTHOR_BUNDLE, MANUSCRIPT / "Figure_legends.docx")
    build_cover_letter(SUBMISSION_SRC / "Cover_letter.docx", MANUSCRIPT / "Cover_letter.docx")
    build_author_bundle(
        MANUSCRIPT / "Clinical_Chemistry_submission.docx",
        MANUSCRIPT / "Tables_main.docx",
        MANUSCRIPT / "Figure_legends.docx",
        MANUSCRIPT / "Clinical_Chemistry_author_bundle.docx",
    )

    supp_src = SUBMISSION_SRC / "Online_Supplement.pdf"
    if supp_src.exists():
        import fitz

        probe = "\n".join(page.get_text() for page in fitz.open(supp_src)[:1])
        if "binary hit-rate verification" in probe:
            shutil.copy2(supp_src, MANUSCRIPT / "Online_Supplement.pdf")
        else:
            patch_online_supplement_pdf(supp_src, MANUSCRIPT / "Online_Supplement.pdf")

    refs_src = SUBMISSION_SRC / "REFERENCES_FINAL_29.txt"
    if refs_src.exists():
        shutil.copy2(refs_src, MANUSCRIPT / "REFERENCES_FINAL_29.txt")

    copy_figures(fig_dir)
    write_manifest()

    # Update submission/ handoff copies.
    for name in [
        "Clinical_Chemistry_submission.docx",
        "Tables_main.docx",
        "Figure_legends.docx",
        "Cover_letter.docx",
        "Clinical_Chemistry_author_bundle.docx",
    ]:
        shutil.copy2(MANUSCRIPT / name, SUBMISSION_SRC / name)

    checks = {
        "main": verify_docx(MANUSCRIPT / "Clinical_Chemistry_submission.docx"),
        "tables": verify_docx(MANUSCRIPT / "Tables_main.docx"),
        "legends": verify_docx(MANUSCRIPT / "Figure_legends.docx"),
        "cover": verify_docx(MANUSCRIPT / "Cover_letter.docx"),
        "bundle": verify_docx(MANUSCRIPT / "Clinical_Chemistry_author_bundle.docx"),
    }
    print(f"Wrote submission bundle to {MANUSCRIPT}")
    for label, c in checks.items():
        print(f"  {label}: {c}")

    main = checks["main"]
    if main["main_table_7"] > 0:
        raise SystemExit("ERROR: main-text Table 7 references remain in main manuscript")
    if main["broken_at_per_arm"] > 0:
        raise SystemExit("ERROR: Brief Summary math still broken (at  per arm)")
    if main["math_blocks"] < 12:
        raise SystemExit(f"ERROR: main manuscript math blocks too low: {main['math_blocks']}")
    if checks["legends"]["math_blocks"] < 40:
        raise SystemExit("ERROR: figure legends math blocks too low")
    if checks["bundle"]["main_table_7"] > 0:
        raise SystemExit("ERROR: author bundle still has main-text Table 7")

    main_xml = zipfile.ZipFile(MANUSCRIPT / "Clinical_Chemistry_submission.docx").read(
        "word/document.xml"
    ).decode("utf-8")
    if main_xml.count("<m:oMathPara>") < 2:
        raise SystemExit("ERROR: Methods Eq. (2) display math missing (need n_approx + p-bar)")
    main_plain_for_eq = re.sub(r"</w:p>", "\n", main_xml)
    main_plain_for_eq = re.sub(r"<[^>]+>", "", main_plain_for_eq)
    methods_region = main_plain_for_eq[
        main_plain_for_eq.find("\nMethods\n") : main_plain_for_eq.find("\nResults\n")
    ]
    if "Eq. 2" not in methods_region and "Eq. (2)" not in methods_region:
        raise SystemExit("ERROR: Methods text no longer labels Eq. (2)")
    if "\nwhere\n" not in methods_region and "where" not in methods_region:
        raise SystemExit("ERROR: Methods Eq. (2) lost the 'where' connector")
    cover_xml = zipfile.ZipFile(MANUSCRIPT / "Cover_letter.docx").read("word/document.xml").decode(
        "utf-8"
    )
    if "folklore  per" in cover_xml:
        raise SystemExit("ERROR: Cover letter still has broken folklore phrase")

    wc = _count_main_text_words(main_xml)
    print(f"  main-text word count (Intro–Discussion): {wc}")
    if wc > 3500:
        raise SystemExit(f"ERROR: main text exceeds Clinical Chemistry 3500-word limit ({wc})")
    if wc < 1500:
        raise SystemExit(f"ERROR: main text unexpectedly short ({wc})")
    refs_start = main_xml.find(">References<")
    if refs_start < 0:
        refs_start = main_xml.find(">References</")
    refs_region = main_xml[refs_start:] if refs_start >= 0 else ""
    if re.search(r"[\u4e00-\u9fff]", refs_region):
        raise SystemExit("ERROR: Chinese characters remain in References section")
    if "CLSI EP17-A2：必须引用" in main_xml:
        raise SystemExit("ERROR: draft Chinese reference notes remain")
    text = re.sub(r"</w:p>", "\n", main_xml)
    text = re.sub(r"<[^>]+>", "", text)
    ref_n = len(re.findall(r"(?m)^\d+\.\s", text[text.find("\nReferences\n") :]))
    print(f"  references: {ref_n}")
    if ref_n != 29:
        raise SystemExit(f"ERROR: expected 29 references, found {ref_n}")
    if "Python $$3.10" in main_xml:
        raise SystemExit("ERROR: Data availability still has Python $$3.10")
    if "Background." not in main_xml or "Conclusions." not in main_xml:
        raise SystemExit("ERROR: structured abstract headings missing")
    text = re.sub(r"</w:p>", "\n", main_xml)
    text = re.sub(r"<[^>]+>", "", text)
    cited: set[int] = set()
    body = text[text.find("\nIntroduction\n") : text.find("\nReferences\n")]
    for m in re.finditer(r"\[([0-9,\-\s]+)\]", body):
        for part in m.group(1).split(","):
            part = part.strip()
            if "-" in part:
                a, b = part.split("-", 1)
                cited.update(range(int(a), int(b) + 1))
            elif part.isdigit():
                cited.add(int(part))
    missing_cites = [i for i in range(1, 30) if i not in cited]
    print(f"  cited refs: {len(cited)}/29; uncited: {missing_cites}")
    if missing_cites:
        raise SystemExit(f"ERROR: uncited references remain: {missing_cites}")

    cover_plain = re.sub(r"</w:p>", "\n", cover_xml)
    cover_plain = re.sub(r"<[^>]+>", "", cover_plain)
    if "Prospective Sample Size Planning" in cover_plain:
        raise SystemExit("ERROR: Cover letter title still mismatches the manuscript")
    if MANUSCRIPT_TITLE not in cover_plain:
        raise SystemExit("ERROR: Cover letter missing current manuscript title")
    header_lines = [ln.strip() for ln in cover_plain.splitlines() if ln.strip()][:4]
    if not any(ln.startswith("Journal:") for ln in header_lines):
        raise SystemExit("ERROR: Cover letter missing Journal: header line")
    if not any(ln.startswith("Title:") for ln in header_lines):
        raise SystemExit("ERROR: Cover letter missing Title: header line")
    if any("Title:" in ln and "Journal:" in ln for ln in header_lines):
        raise SystemExit("ERROR: Cover letter header still jammed on one line")
    if "phonetic" in cover_plain.lower():
        raise SystemExit("ERROR: Cover letter still mentions phonetic name")
    if re.search(r"(?<!Supplementary )Tables 1, 3, 7", cover_plain):
        raise SystemExit("ERROR: Cover letter still lists Tables 1, 3, 7")
    if "Tables 1–3" not in cover_plain and "Tables 1-3" not in cover_plain:
        raise SystemExit("ERROR: Cover letter missing Tables 1–3 wording")

    supp_path = MANUSCRIPT / "Online_Supplement.pdf"
    if supp_path.exists():
        import fitz

        supp_text = "\n".join(page.get_text() for page in fitz.open(supp_path))
        if "Prospective Sample Size Planning for Limit of Detection" in supp_text:
            raise SystemExit("ERROR: Online_Supplement.pdf still has old title")
        if "Tables 1, 3, 7" in supp_text:
            raise SystemExit("ERROR: Online_Supplement.pdf still lists Tables 1, 3, 7")
        if "binary hit-rate verification" not in supp_text and "hit-rate verification of detection" not in supp_text:
            raise SystemExit("ERROR: Online_Supplement.pdf missing current title")
        if "Tables 1-3" not in supp_text and "Tables 1–3" not in supp_text:
            raise SystemExit("ERROR: Online_Supplement.pdf missing Tables 1-3 wording")
        print("  supplement: rebuilt companion PDF")
    print("Submission bundle verification passed.")


if __name__ == "__main__":
    main()
