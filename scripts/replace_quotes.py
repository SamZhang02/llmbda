import re
import os

DOUBLE_QUOTED_COURSE_CODE_PATTERN = re.compile(
    r"\"[A-Z0-9]{4} [0-9]{3}(?:D1|D2|N1|N2|J1|J2|J3)?\""
)

with open(os.path.join("dataset", "labelled.csv", "r")) as f:
    lines = f.readlines()


with open(os.path.join("dataset", "labelled.csv", "w")) as f:
    fixed = []

    for line in lines:
        if not fixed:
            fixed.append(line)
            continue

        codes = re.findall(DOUBLE_QUOTED_COURSE_CODE_PATTERN, line)

        for code in codes:
            line = line.replace(code, code.replace('"', "'"))

        line = line.replace('"&"', "'&'").replace('"|"', "'|'")

        fixed.append(line)

    f.writelines(fixed)
