.PHONY: validate test check

validate:
	python3 -m scripts.validate_catalog
	python3 -m scripts.validate_geodata

test:
	python3 -m unittest discover -v

check: validate test
