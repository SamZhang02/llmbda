import json
import regex as re


def clean_html(text):
    return re.sub('<[^<]+?>', '', text)


COURSE_CODE_PATTERN = re.compile(
    r"([A-Z0-9]{4} [0-9]{3}(?:D1|D2|N1|N2|J1|J2|J3)?)"
)

def run():

    indices = []
    course_codes = []
    req_type = []
    reqs = []
    tree = []

    index = 1 
    
    with open('./courses-2023-2024.json') as f:
        courses = json.load(f)

        for course in courses:
            prereq = course['prerequisitesText'] 
            coreq = course['corequisitesText']

            if prereq and re.search(COURSE_CODE_PATTERN,prereq):
                course_codes.append(course['_id'])
                req_type.append(1)
                reqs.append(clean_html(prereq))
                indices.append(index)
                index += 1
                
                codes = re.findall(COURSE_CODE_PATTERN, prereq)
                if len(codes) > 1:
                    tree.append("[]")
                else:
                    tree.append(f'["{codes[0]}"]')



            if coreq and re.search(COURSE_CODE_PATTERN,coreq):
                course_codes.append(course['_id'])
                req_type.append(2)
                reqs.append(clean_html(coreq))
                indices.append(index)
                index += 1

                codes = re.findall(COURSE_CODE_PATTERN, coreq)
                if len(codes) > 1:
                    tree.append("[]")
                elif len(codes) == 1:
                    tree.append(f'["{codes[0]}"]')

    with open('./requisites.csv', 'w') as csv:
        csv.write('index,course,req_type,requisite, requisite_tree\n')
        for i in range(len(indices)):
            csv.write(f'{indices[i]},"{course_codes[i]}",{req_type[i]},"{reqs[i]}", "{tree[i]}"\n')

if __name__ == '__main__':
    run()


