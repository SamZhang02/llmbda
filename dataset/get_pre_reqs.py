import json
import regex as re


def clean_html(text):
    return re.sub("<[^<]+?>", "", text)


COURSE_CODE_PATTERN = re.compile(r"([A-Z0-9]{4} [0-9]{3}(?:D1|D2|N1|N2|J1|J2|J3)?)")

COURSE_NUMBER_PATTERN = re.compile(r"([0-9]{3}(?:D1|D2|N1|N2|J1|J2|J3)?)")


def run():
    indices = []
    course_codes = []
    req_type = []
    reqs = []
    object_tree = []
    json_tree = []

    index = 1

    with open("./courses-2023-2024.json") as f:
        courses = json.load(f)

        for course in courses:
            prereq = (
                clean_html(course["prerequisitesText"])
                if course["prerequisitesText"]
                else None
            )
            coreq = (
                clean_html(course["corequisitesText"])
                if course["corequisitesText"]
                else None
            )

            if prereq and re.search(COURSE_CODE_PATTERN, prereq):
                course_codes.append(course["_id"])
                req_type.append(1)
                reqs.append(prereq)
                indices.append(index)
                index += 1

                codes = re.findall(COURSE_CODE_PATTERN, prereq)
                numbers = re.findall(COURSE_NUMBER_PATTERN, prereq)

                if len(codes) == 1 and len(numbers) == 1:
                    object_tree.append(f'["{codes[0]}"]')
                    json_tree.append(json.dumps({"prerequisites": codes[0]}))
                else:
                    object_tree.append("[]")
                    json_tree.append("{}")

            if coreq and re.search(COURSE_CODE_PATTERN, coreq):
                course_codes.append(course["_id"])
                req_type.append(2)
                reqs.append(coreq)
                indices.append(index)
                index += 1

                codes = re.findall(COURSE_CODE_PATTERN, coreq)
                numbers = re.findall(COURSE_NUMBER_PATTERN, coreq)

                if len(codes) == 1 and len(numbers) == 1:
                    object_tree.append(f'["{codes[0]}"]')
                    json_tree.append(json.dumps({"corequisites": codes[0]}))
                else:
                    object_tree.append("[]")
                    json_tree.append("{}")

    with open("./requisites.csv", "w") as csv:
        csv.write("index,course,req_type,requisite, object_tree, json_tree\n")
        for i in range(len(indices)):
            csv.write(
                f'{indices[i]},"{course_codes[i]}",{req_type[i]},"{reqs[i]}", "{object_tree[i]},"{json_tree[i]}"\n'
            )

        print(
            f"Auto-labeled {len([leaf for leaf in object_tree if leaf != '[]'])} leaves."
        )


if __name__ == "__main__":
    run()
