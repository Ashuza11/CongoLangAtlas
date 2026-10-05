.PHONY: validate test check

validate:
	python3 -m scripts.validate_catalog

test:
	python3 -m unittest discover -v

check: validate test
