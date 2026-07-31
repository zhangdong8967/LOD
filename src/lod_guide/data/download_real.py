"""Download publicly available LoD-related datasets into data/raw/."""

from __future__ import annotations

import io
import json
import shutil
import subprocess
import tarfile
import tempfile
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

from lod_guide.data.parsers import (
    load_anion_ic_csv,
    load_carobene_lombardy_eqa_csv,
    load_cation_ic_csv,
    load_cptac_msstats_lobd_csv,
    load_ep17_estradiol_xlsx,
    load_ep17_probit_xlsx,
    load_ep17_troponin_xlsx,
    load_radioimmuno_linearity_txt,
    load_radioimmuno_lod_txt,
    load_radioimmuno_precision_txt,
    load_rmn_qualification_xlsx,
    load_zenodo_qpcr_cq,
    parse_real_dataset,
)

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "data" / "raw"

_UA = "Mozilla/5.0 (compatible; lod-guide/0.4; +https://local/lod-guide)"


@dataclass(frozen=True)
class RemoteDataset:
    dataset_id: str
    filename: str
    url: str
    citation: str
    result_family: str
    license_note: str = ""
    evidence_tier: str = "A"  # A=raw replicates; B=summary; C=synthetic demo
    download_kind: str = "file"  # file | zip_csv | bioc_rda_csv


REMOTE_DATASETS: tuple[RemoteDataset, ...] = (
    RemoteDataset(
        dataset_id="zenodo_mus_wt_qpcr",
        filename="zenodo_mus_wt_lod_loq.csv",
        url="https://zenodo.org/records/12609243/files/Data%20-%20Mus%20WT%20assay%20-%20LOD-LOQ.csv?download=1",
        citation="Zenodo 12609243 — Mus WT qPCR LoD/LoQ (Cq vs copy number).",
        result_family="qpcr_cq_continuous",
        license_note="See Zenodo record",
        evidence_tier="A",
    ),
    RemoteDataset(
        dataset_id="zenodo_mus_multiplex_qpcr",
        filename="zenodo_mus_multiplex_lod_loq.csv",
        url="https://zenodo.org/records/12609243/files/Data%20-%20Mus%20WT%20and%20tCRISPR%20multiplex%20LOD-LOQ.csv?download=1",
        citation="Zenodo 12609243 — multiplex tCRISPR/WT qPCR LoD/LoQ.",
        result_family="qpcr_cq_continuous",
        license_note="See Zenodo record",
        evidence_tier="A",
    ),
    RemoteDataset(
        dataset_id="analyseit_ep17_estradiol",
        filename="EP17-A2-Example-1.xlsx",
        url="https://analyse-it.com/products/examples/EP17-A2-Example-1.xlsx",
        citation=(
            "CLSI EP17-A2 Appendix A estradiol example (Analyse-it workbook): "
            "immunoassay continuous blank + low-level replicates."
        ),
        result_family="immunoassay_continuous",
        license_note="Free Analyse-it example; cite CLSI EP17-A2 for republication",
        evidence_tier="A",
    ),
    RemoteDataset(
        dataset_id="analyseit_ep17_probit",
        filename="EP17-A2-Example-4.xlsx",
        url="https://analyse-it.com/products/examples/EP17-A2-Example-4.xlsx",
        citation=(
            "CLSI EP17-A2 Appendix C probit/hit-rate example (Analyse-it): "
            "concentration x detect outcomes."
        ),
        result_family="probit_hit_rate",
        license_note="Free Analyse-it example; cite CLSI EP17-A2",
        evidence_tier="A",
    ),
    RemoteDataset(
        dataset_id="analyseit_ep17_troponin_precision",
        filename="EP17-A2-Example-3.xlsx",
        url="https://analyse-it.com/products/examples/EP17-A2-Example-3.xlsx",
        citation=(
            "CLSI EP17-A2 Appendix D troponin I precision-profile pools "
            "(Analyse-it; generated to match target Mean/SD) — LoQ-style."
        ),
        result_family="cardiac_precision_profile",
        license_note="Synthetic EP17 demo; cite Analyse-it / CLSI EP17-A2",
        evidence_tier="C",
    ),
    RemoteDataset(
        dataset_id="zenodo_cation_ic_lod",
        filename="LOD_LOQ_cations.csv",
        url="https://zenodo.org/api/records/5909650/files/LOD_LOQ_cations.csv/content",
        citation="Dierendonck C. Cation LOD/LOQ (Zenodo 5909650). CC-BY-4.0.",
        result_family="analytical_chemistry_ic",
        license_note="CC-BY-4.0",
        evidence_tier="B",
    ),
    RemoteDataset(
        dataset_id="zenodo_anion_ic_lod",
        filename="LOD_LOQ_anions.csv",
        url="https://zenodo.org/api/records/5901444/files/LOD_LOQ_anions.csv/content",
        citation="Dierendonck C. Anion LOD/LOQ (Zenodo 5901444). CC-BY-4.0.",
        result_family="analytical_chemistry_ic",
        license_note="CC-BY-4.0",
        evidence_tier="B",
    ),
    RemoteDataset(
        dataset_id="mendeley_carobene_lombardy_eqa",
        filename="Carobene_Lombardy_EQA_clinical_chemistry.csv",
        url="https://data.mendeley.com/public-api/zip/r4szpw8sn5/download/1",
        citation=(
            "Carobene A. et al. Commutability of Lombardy Region EQA control materials "
            "for enzymes, calcium, and creatinine (Clin Chim Acta 2025; Mendeley "
            "10.17632/r4szpw8sn5). Ten labs; ALT/AST/ALP/CK/LDH/creatinine/calcium raw replicates. CC-BY-4.0."
        ),
        result_family="clinical_chemistry_multilab",
        license_note="CC-BY-4.0",
        evidence_tier="A",
        download_kind="zip_csv",
    ),
    RemoteDataset(
        dataset_id="bioc_msstats_lobd_cptac",
        filename="CPTAC_MSstatsLOBD_calibration_raw.csv",
        url="https://bioconductor.org/packages/release/bioc/src/contrib/MSstatsLOBD_1.20.0.tar.gz",
        citation=(
            "CPTAC Assay Portal peptide spike-in (JHU_DChan_HZhang_ZZhang) via Bioconductor "
            "MSstatsLOBD::raw_data (Galitzine et al., Mol Cell Proteomics 2018; Artistic-2.0). "
            "43 peptides × blank (Concentration=0) + concentration grid — proteomics blank–LoB."
        ),
        result_family="proteomics_blank_lob",
        license_note="Artistic-2.0 (Bioconductor MSstatsLOBD)",
        evidence_tier="A",
        download_kind="bioc_rda_csv",
    ),
    RemoteDataset(
        dataset_id="zenodo_radioimmuno_lod_summary",
        filename="LOD_radioimmuno.txt",
        url="https://zenodo.org/api/records/12664367/files/LOD.txt/content",
        citation=(
            "Malkamäki et al. radioimmuno-dot-blot LOD summaries (Anal. Chem.; Zenodo 12664367). "
            "Tier B blank mean/SD summaries."
        ),
        result_family="radioimmuno_summary",
        license_note="CC-BY-4.0",
        evidence_tier="B",
    ),
    RemoteDataset(
        dataset_id="zenodo_radioimmuno_precision",
        filename="Precision_radioimmuno.txt",
        url="https://zenodo.org/api/records/12664367/files/Precision.txt/content",
        citation=(
            "Malkamäki et al., Anal. Chem. 10.1021/acs.analchem.4c03393; Zenodo 12664367 "
            "Precision.txt — per-sample replicate mean/SD/CV (CC-BY-4.0)."
        ),
        result_family="radioimmuno_precision_profile",
        license_note="CC-BY-4.0",
        evidence_tier="A",
    ),
    RemoteDataset(
        dataset_id="zenodo_radioimmuno_linearity",
        filename="Linearity_1_radioimmuno.txt",
        url="https://zenodo.org/api/records/12664367/files/Linearity_1.txt/content",
        citation=(
            "Malkamäki et al., Anal. Chem.; Zenodo 12664367 Linearity_1.txt — "
            "concentration (ng) × DPM replicates (CC-BY-4.0)."
        ),
        result_family="radioimmuno_linearity_continuous",
        license_note="CC-BY-4.0",
        evidence_tier="A",
    ),
    RemoteDataset(
        dataset_id="zenodo_rmn_qualification",
        filename="RMN_Assay_Qualification_Dataset_v1.xlsx",
        url="https://zenodo.org/api/records/17108929/files/RMN_Assay_Qualification_Dataset_v1.xlsx/content",
        citation=(
            "Sawant, Harit, Tomaras. RMN assay qualification dataset "
            "(Zenodo 10.5281/zenodo.17108929). Replicate ID50 by dilution; CC-BY-4.0."
        ),
        result_family="rmn_microneutralization_continuous",
        license_note="CC-BY-4.0",
        evidence_tier="A",
    ),
)


def ensure_raw_dir() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    return RAW_DIR


def _extract_bioc_rda_to_csv(tarball: bytes, *, rda_name: str, object_name: str, out_csv: Path) -> Path:
    """Extract *.rda from a Bioconductor source tarball and export via Rscript."""
    if shutil.which("Rscript") is None:
        raise OSError(
            "Rscript not found; cannot convert Bioconductor .rda to CSV. "
            "Install R, or place the CSV at data/raw/ manually."
        )
    with tempfile.TemporaryDirectory(prefix="lod_guide_bioc_") as tmp:
        tmp_path = Path(tmp)
        tar_path = tmp_path / "pkg.tar.gz"
        tar_path.write_bytes(tarball)
        with tarfile.open(tar_path, "r:gz") as tf:
            members = [m for m in tf.getmembers() if m.name.endswith(f"/data/{rda_name}")]
            if not members:
                raise OSError(f"No data/{rda_name} in Bioconductor tarball")
            try:
                tf.extract(members[0], tmp_path, filter="data")
            except TypeError:
                tf.extract(members[0], tmp_path)
            rda_path = tmp_path / members[0].name
        script = tmp_path / "export.R"
        script.write_text(
            (
                f'load("{rda_path.as_posix()}")\n'
                f'if (!exists("{object_name}")) stop("object {object_name} missing")\n'
                f'write.csv({object_name}, "{out_csv.as_posix()}", row.names = FALSE)\n'
            ),
            encoding="utf-8",
        )
        proc = subprocess.run(
            ["Rscript", str(script)],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0 or not out_csv.exists() or out_csv.stat().st_size == 0:
            raise OSError(f"Rscript export failed: {proc.stderr or proc.stdout or 'unknown'}")
    return out_csv


def download_dataset(ds: RemoteDataset, *, force: bool = False, timeout: float = 90.0) -> Path:
    ensure_raw_dir()
    path = RAW_DIR / ds.filename
    if path.exists() and not force and path.stat().st_size > 0:
        return path
    req = urllib.request.Request(ds.url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    if ds.download_kind == "zip_csv":
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            members = [n for n in zf.namelist() if n.lower().endswith(".csv") and not n.endswith("/")]
            if not members:
                raise OSError(f"No CSV in zip for {ds.dataset_id}")
            member = max(members, key=lambda n: zf.getinfo(n).file_size)
            path.write_bytes(zf.read(member))
        return path
    if ds.download_kind == "bioc_rda_csv":
        # MSstatsLOBD ships CPTAC calibration as raw_data.rda
        return _extract_bioc_rda_to_csv(
            data,
            rda_name="raw_data.rda",
            object_name="raw_data",
            out_csv=path,
        )
    path.write_bytes(data)
    return path


def download_all_real(*, force: bool = False) -> dict[str, Path | Exception]:
    out: dict[str, Path | Exception] = {}
    for ds in REMOTE_DATASETS:
        try:
            out[ds.dataset_id] = download_dataset(ds, force=force)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            out[ds.dataset_id] = exc
    write_evidence_manifest(out)
    return out


def write_evidence_manifest(results: dict[str, Path | Exception]) -> Path:
    ensure_raw_dir()
    meta = []
    for ds in REMOTE_DATASETS:
        path_or_err = results.get(ds.dataset_id)
        ok = isinstance(path_or_err, Path) and path_or_err.exists()
        meta.append(
            {
                "dataset_id": ds.dataset_id,
                "result_family": ds.result_family,
                "evidence_tier": ds.evidence_tier,
                "citation": ds.citation,
                "license_note": ds.license_note,
                "filename": ds.filename,
                "downloaded": ok,
                "error": None if ok else str(path_or_err),
                "bytes": path_or_err.stat().st_size if ok else 0,
            }
        )
    out = RAW_DIR / "evidence_manifest.json"
    out.write_text(json.dumps({"version": "0.4", "datasets": meta}, indent=2), encoding="utf-8")
    return out


__all__ = [
    "RAW_DIR",
    "REMOTE_DATASETS",
    "RemoteDataset",
    "download_all_real",
    "download_dataset",
    "ensure_raw_dir",
    "load_zenodo_qpcr_cq",
    "load_ep17_estradiol_xlsx",
    "load_ep17_probit_xlsx",
    "load_ep17_troponin_xlsx",
    "load_cation_ic_csv",
    "load_anion_ic_csv",
    "load_carobene_lombardy_eqa_csv",
    "load_cptac_msstats_lobd_csv",
    "load_radioimmuno_lod_txt",
    "load_radioimmuno_precision_txt",
    "load_radioimmuno_linearity_txt",
    "load_rmn_qualification_xlsx",
    "parse_real_dataset",
    "write_evidence_manifest",
]


if __name__ == "__main__":
    results = download_all_real()
    for k, v in results.items():
        print(k, "->", v)
