"""
Transparent audit trail for lod_guide analyses.

Every guidance run can emit a canonical JSON record and SHA-256 hash so that
mathematicians and statisticians can independently recompute decisions.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_DIR = Path(__file__).resolve().parents[3] / "data" / "audit"


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


def sha256_hex(obj: Any) -> str:
    return hashlib.sha256(_canonical_json(obj).encode("utf-8")).hexdigest()


@dataclass
class AuditStep:
    step_id: str
    name: str
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    notes: str = ""


@dataclass
class AuditRecord:
    created_utc: str
    software_version: str
    protocol_id: str
    estimand: dict[str, Any]
    steps: list[AuditStep] = field(default_factory=list)
    final: dict[str, Any] = field(default_factory=dict)
    proposition_certificates: list[dict[str, Any]] = field(default_factory=list)

    def add_step(self, step: AuditStep) -> None:
        self.steps.append(step)

    def to_dict(self) -> dict[str, Any]:
        return {
            "created_utc": self.created_utc,
            "software_version": self.software_version,
            "protocol_id": self.protocol_id,
            "estimand": self.estimand,
            "steps": [asdict(s) for s in self.steps],
            "final": self.final,
            "proposition_certificates": self.proposition_certificates,
        }

    def content_hash(self) -> str:
        # Hash without created_utc for reproducibility across clock times if needed:
        # default includes timestamp; use freeze via protocol for papers.
        payload = self.to_dict()
        return sha256_hex(payload)

    def save(self, path: Path | None = None) -> Path:
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        d = self.to_dict()
        digest = sha256_hex({k: v for k, v in d.items() if k != "created_utc"})
        d["sha256_content"] = digest
        d["sha256_full"] = sha256_hex(d)
        path = path or AUDIT_DIR / f"audit_{digest[:16]}.json"
        path.write_text(json.dumps(d, indent=2, ensure_ascii=True, default=str), encoding="utf-8")
        return path


def new_audit(protocol_id: str, estimand: dict[str, Any]) -> AuditRecord:
    from lod_guide import __version__

    return AuditRecord(
        created_utc=datetime.now(timezone.utc).isoformat(),
        software_version=__version__,
        protocol_id=protocol_id,
        estimand=estimand,
    )
