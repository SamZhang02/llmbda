import csv
import re
import ast
import sys

COURSE_CODE_PATTERN = re.compile(r"([A-Z0-9]{4} [0-9]{3}(?:D1|D2|N1|N2|J1|J2|J3)?)")


def load_csv(csv_file):
    with open(csv_file, "r", newline="") as file:
        csv_reader = csv.DictReader(file)
        return [row for row in csv_reader]


def validate(node):
    match node:
        case str():
            m = COURSE_CODE_PATTERN.fullmatch(node)
            if m is None:
                raise ValueError(f"Invalid course code {m}")
        case list():
            if node[0] not in ["&", "|"]:
                raise ValueError(f"Invalid operator {node[0]}")

            if len(node) < 3:
                raise ValueError("Tree node must have at least 2 children")

            for child in node[1:]:
                validate(child)


data = load_csv("labelled.csv")

errors = 0
for row in data[:100]:
    try:
        tree = ast.literal_eval(row["object_tree"])
    except Exception as e:
        print(
            f"(Index {row['index']}) Failed to parse object_tree for {row['course']}: {e}",
            file=sys.stderr,
        )
        errors += 1
        continue

    if tree == []:
        continue

    try:
        validate(tree)
    except ValueError as e:
        print(
            f"(Index {row['index']}) Validation error for {row['course']}: {e}",
            file=sys.stderr,
        )
        errors += 1

if errors > 0:
    print(f"Data validation failed for {errors}")
    sys.exit(1)

print("Labelled data passed validation.")
