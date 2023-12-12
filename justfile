default:
  just --list

validate:
  poetry run python3 dataset/check.py dataset/labelled.csv

eval model_name ans_path pred_path:
  poetry run python3 scripts/eval.py {{model_name}} {{ans_path}} {{pred_path}} \
  --log_result "eval/{{model_name}}.txt" \
  --ans_text_field object_tree \
  --pred_text_field predictions \
  --join_on index \


