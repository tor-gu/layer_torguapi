export PYTHONPATH = src

src_dirs := src tests

style:
	python -m isort $(src_dirs)
	python -m black --target-version py39 $(src_dirs)

test:
	python -m pytest -sv tests/

build:
	python -m build

all: style test build

