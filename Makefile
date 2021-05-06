.PHONY: all

.ONESHELL:
SHELL := /bin/bash

SRC = $(wildcard **/*.ipynb)

all: nbdev docs_serve

nbdev: $(SRC)
	nbdev_build_lib
	touch nbs/index.ipynb

docs_serve: docs
	killport 4001
	cd docs && bundle exec jekyll serve --port 4001

docs: $(SRC)
	nbdev_build_docs
	touch docs/index.html

test:
	nbdev_test_nbs --flags ''

release: pypi
	fastrelease_conda_package --mambabuild --upload_user fastai
	nbdev_bump_version

conda_release:
	fastrelease_conda_package --mambabuild --upload_user fastai

pypi: dist
	twine upload --repository pypi dist/*

dist: clean
	python setup.py sdist bdist_wheel

clean:
	rm -rf dist