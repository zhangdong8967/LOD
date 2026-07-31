"""Paper artifact registry, LoQ tables, and internal review builders."""

from lod_guide.paper.registry import FIGURES, TABLES, write_caption_files

__all__ = ["FIGURES", "TABLES", "write_caption_files", "build_paper_artifacts"]


def build_paper_artifacts(*args, **kwargs):
    """Lazy import to avoid circular dependency with lod_guide.figures."""
    from lod_guide.paper.build_artifacts import build_paper_artifacts as _build

    return _build(*args, **kwargs)
