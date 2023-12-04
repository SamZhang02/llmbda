import json
import re
import os
from dataclasses import dataclass


def clean_html(text):
    return re.sub("<[^<]+?>", "", text)


COURSE_CODE_PATTERN = re.compile(r"([A-Z0-9]{4} [0-9]{3}(?:D1|D2|N1|N2|J1|J2|J3)?)")

COURSE_NUMBER_PATTERN = re.compile(r"([0-9]{3}(?:D1|D2|N1|N2|J1|J2|J3)?)")


@dataclass
class CourseInfo:
    index: int
    course: str
    req_type: int
    requisite: str
    object_tree: str = "[]"
    json_tree: str = "{}"


def run():
    autolabelled: list[CourseInfo] = []
    to_label: list[CourseInfo] = []

    index = 1

    with open(os.path.join("dataset", "courses-2023-2024.json")) as f:
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
                course_info = CourseInfo(
                    index=index, course=course["_id"], req_type=1, requisite=prereq
                )
                index += 1

                codes = re.findall(COURSE_CODE_PATTERN, prereq)
                numbers = re.findall(COURSE_NUMBER_PATTERN, prereq)

                if len(codes) == 1 and len(numbers) == 1:
                    course_info.object_tree = f'["{codes[0]}"]'
                    course_info.json_tree = json.dumps({"prerequisites": codes[0]})
                    autolabelled.append(course_info)
                else:
                    to_label.append(course_info)

            if coreq and re.search(COURSE_CODE_PATTERN, coreq):
                course_info = CourseInfo(
                    index=index, course=course["_id"], req_type=2, requisite=coreq
                )
                index += 1

                codes = re.findall(COURSE_CODE_PATTERN, coreq)
                numbers = re.findall(COURSE_NUMBER_PATTERN, coreq)

                if len(codes) == 1 and len(numbers) == 1:
                    course_info.object_tree = f'["{codes[0]}"]'
                    course_info.json_tree = json.dumps({"corequisites": codes[0]})
                    autolabelled.append(course_info)
                else:
                    to_label.append(course_info)

    with open(os.path.join("dataset", "autolabelled.csv"), "w") as csv:
        csv.write("index,course,req_type,requisite,object_tree,json_tree\n")
        for c in autolabelled:
            csv.write(
                f'{c.index},"{c.course}",{c.req_type},"{c.requisite}","{c.object_tree}","{c.json_tree}"\n'
            )

        print(f"Auto-labeled {len(autolabelled)} leaves.")

    with open(os.path.join("dataset", "autolabelled.csv"), "w") as csv:
        csv.write("index,course,req_type,requisite,object_tree,json_tree\n")
        for c in to_label:
            csv.write(
                f'{c.index},"{c.course}",{c.req_type},"{c.requisite}","{c.object_tree}","{c.json_tree}"\n'
            )
        print(f"{len(to_label)} left to label.")


if __name__ == "__main__":
    run()
