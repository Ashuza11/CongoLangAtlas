.PHONY: validate test check geodata places presence-candidates import-congolangbench review-congolangbench discover-sources web-data

CONGOLANGBENCH ?= ../DRCongo_Lang_Benchmark

validate:
	python3 -m scripts.validate_catalog
	python3 -m scripts.validate_geodata
	python3 -m scripts.validate_reviews
	python3 -m scripts.validate_presence

test:
	python3 -m unittest discover -v

check: validate test

geodata:
	python3 -m scripts.build_geodata

places:
	python3 -m scripts.build_place_catalog

presence-candidates:
	python3 -u -m scripts.build_presence_candidates

import-congolangbench:
	python3 -m scripts.import_congolangbench "$(CONGOLANGBENCH)"

review-congolangbench:
	python3 -m scripts.build_import_review_queue

discover-sources:
	python3 -u -m scripts.discover_sources

web-data:
	python3 -m scripts.build_web_data
