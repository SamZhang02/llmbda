import re

DOUBLE_QUOTED_COURSE_CODE_PATTERN = re.compile(r'\"[A-Z0-9]{4} [0-9]{3}(?:D1|D2|N1|N2|J1|J2|J3)?\"')

with open('./labelled.csv','r') as f:  
    lines = f.readlines()


with open('./labelled.csv',"w") as f:
    fixed = []

    for line in lines:
        if not fixed:
            fixed.append(line)
            continue

        codes = [x for x in re.findall(DOUBLE_QUOTED_COURSE_CODE_PATTERN,line)]

        for code in codes:
            line = line.replace(code, code.replace("\"", "\'"))\
                .replace("\"&\"", "\'&\'")\
                .replace("\"|\"", "\'|\'")
        fixed.append(line)


    f.writelines(fixed)

