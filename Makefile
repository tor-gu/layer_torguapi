export PYTHONPATH = src

src_dirs := src tests scripts

style:
	python -m isort $(src_dirs)
	python -m black --target-version py39 $(src_dirs)

test:
	python -m pytest -sv tests/

build:
	python -m build

# The Lambda layer zip that infra/ publishes
layer:
	python scripts/build_layer.py

all: style test build

