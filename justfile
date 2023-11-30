default:
  just --list

validate:
  python3 dataset/check.py dataset/labelled.csv
