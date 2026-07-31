.PHONY: paper-artifacts test deep-research download install run run-all theory-verify theory-pdf fig1-tikz clean-outputs

install:
	pip install -e ".[dev]"

# One-click full pipeline (preferred entry point)
run:
	./run.sh

test:
	python -m pytest -q

download:
	python -m lod_guide.data.download_real

deep-research:
	python examples/run_deep_research.py

theory-verify:
	python examples/run_theory_verification.py

# One-click: theory + deep research + scenarios + transparent analysis + paper artifacts
run-all:
	./run.sh

run-all-quick:
	./run.sh --quick

# One-click manuscript artifact package (captions, tables, review, figure copies)
paper-artifacts:
	python examples/run_paper_artifacts.py

# Compile manuscript/THEORY_MONOGRAPH.pdf (needs pdflatex or Docker)
theory-pdf:
	./scripts/build_theory_monograph.sh

fig1-tikz:
	./scripts/fig1_tikz.sh

clean-outputs:
	python scripts/clean_outputs.py --apply

all-analyses: run-all
