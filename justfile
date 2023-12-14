default:
  just --list

alias f := fmt

fmt:
  ruff format . && isort .

validate:
  python3 dataset/check.py dataset/labelled.csv
