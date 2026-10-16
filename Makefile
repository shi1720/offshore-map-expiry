PYTHON ?= python3

.PHONY: download reproduce paper
download:
	$(PYTHON) src/download_data.py

reproduce:
	$(PYTHON) src/analyze.py
	$(PYTHON) src/additional.py
	$(PYTHON) src/verify_independent.py
	$(PYTHON) -m pytest tests -q
	$(PYTHON) src/report.py

paper:
	cd paper && tectonic main.tex
	cp paper/main.pdf paper/When_Portfolio_Maps_Go_Stale_Shivam_Gupta.pdf
