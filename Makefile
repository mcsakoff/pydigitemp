PROJECT = digitemp

VERSION := $(shell [ -e bin/python ] && bin/python -c "from $(PROJECT) import __version__; print(__version__)")

.PHONY: help version package release develop test clobber
default: help

END = \x1b[0m
RED = \x1b[31;01m
GRN = \x1b[32;01m
YEL = \x1b[33;01m
BLU = \x1b[34;01m

help: Makefile
	@echo "$(GRN)Choose a command run:$(END)"
	@sed -n 's/^## //p' $< | column -t -s ':' | sed -e 's/^/    /'
	@echo

## version: Print current version
version:
	@echo '$(PROJECT) $(VERSION)'

## package: Create a package
package:
	@echo "$(GRN)--> Building package$(END)"
	@bin/python setup.py sdist

## release: Upload a package to pypi.org
release: dist/$(PROJECT)-$(VERSION).tar.gz bin/twine package
	@echo "$(GRN)--> Uploading package $(PROJECT) $(VERSION)$(END)"
	@bin/twine upload $<

## develop: (Re)Install the module in develop mode
develop: bin/python
	@echo "$(GRN)--> Installing $(PROJECT)$(END)"
	@bin/pip install --upgrade pip setuptools
	@bin/pip install -e .

## test: Run unit-tests
test: bin/pytest
	@echo "$(GRN)--> Running tests$(END)"
	@bin/pytest -v $(PROJECT) -W ignore

## clobber: Cleanup EVERYTHING
clobber:
	@rm -rf bin dist include lib pyvenv.cfg pip-selfcheck.json $(PROJECT).egg-info py$(PROJECT).egg-info .pytest_cache


bin/twine: bin/python
	@echo "$(GRN)--> Installing twine$(END)"
	@bin/pip install --upgrade twine
	@touch bin/twine

bin/pytest: bin/python
	@echo "$(GRN)--> Installing pytest$(END)"
	@bin/pip install --upgrade pytest
	@touch bin/pytest

bin/python:
	@echo "$(GRN)--> Creating Python virtual environment$(END)"
	@python3 -m venv .
	@touch bin/python
