.PHONY: validate test check geodata import-congolangbench

CONGOLANGBENCH ?= ../DRCongo_Lang_Benchmark

validate:
	python3 -m scripts.validate_catalog
	python3 -m scripts.validate_geodata

test:
	python3 -m unittest discover -v

check: validate test

geodata:
	python3 -m scripts.build_geodata

import-congolangbench:
	python3 -m scripts.import_congolangbench "$(CONGOLANGBENCH)"
