default:
  just --list

alias f := fmt

fmt:
  ruff format . && isort .

deps:
  poetry install --no-root

validate:
  poetry run python3 dataset/check.py dataset/labelled.csv

eval model_name pred_path:
  poetry run python3 eval.py {{model_name}} dataset/test.csv {{pred_path}} \
  --log_result "eval/{{model_name}}.txt" \
  --ans_text_field object_tree \
  --pred_text_field predictions \
  --join_on index \
