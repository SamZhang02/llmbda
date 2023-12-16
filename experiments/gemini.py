import os
import typing as t

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv

PROMPT = "Parse the following list of course requirements into a logic expression tree structure. Each node is represented by an string or array. Non-leaf nodes are arrays, and represent nodes for logical operators. The first element in the array is a logical operator. AND should be represented by '&', and OR should be represented by '|'. The rest of the elements in the array are the children. Logical expressions should only ever be in the first element of the array. Every non-leaf node should have at least two children. Leaf nodes are strings, never arrays. Leaf node values are the course codes in the requirements. These are only allowed to be valid course codes, not any arbitrary string. As such, you should ignore things like 'equivalent' or 'permission of instructor', these should never be included in the output. A valid course code is 4 uppercase/numeric characters followed by a space, then a 3 digit number. Use single quotes for strings. If there is only a single node in the tree (one leaf) just output the course code by itself as a string, not a single element array.  Do not give any explanation, just output the parsed data."


class Model:
    def __init__(self, model):
        self.model = model

    @staticmethod
    def initialize():
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

        config = {
            "temperature": 0,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }

        settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
        ]

        return Model(
            genai.GenerativeModel(
                model_name="gemini-pro",
                generation_config=config,
                safety_settings=settings,
            )
        )

    def prompt(self, parts: t.List[str]) -> str:
        return self.model.generate_content(parts).text

    def zero_shot(self, dataset: pd.DataFrame):
        reqs = dataset["requisite"]
        expected = dataset["object_tree"]

        predictions = []

        for i, (req, label) in enumerate(zip(reqs, expected)):
            try:
                prediction = self.prompt([PROMPT + "\n" + req])
                print("Predicted: ", prediction)
                print("Actual: ", label)
                print(f"({i}/{len(reqs)})")
                prediction = prediction.replace("\n", "")
                predictions.append(prediction)
            except Exception as e:
                print(f"error: {e}")
                predictions.append("")
                continue

        out = {"index": dataset["index"], "predictions": predictions}
        df = pd.DataFrame(out)
        df.to_csv(os.path.join("results", "gemini-zero-shot.csv"), index=False)

    def one_shot(self, dataset: pd.DataFrame):
        reqs = dataset["requisite"]
        expected = dataset["object_tree"]

        predictions = []

        extended_prompt = (
            PROMPT
            + """
        Here's some examples, marked with input and expected output.

        ---INPUT---
        Prerequisite: PHGY 311
        ---OUTPUT---
        'PHGY 311'

        ---INPUT---
        Prerequisite: URBP 622 or permission of instructor.
        ---OUTPUT---
        'URBP 622'

        ---INPUT---
        Prerequisites: ECSE 205, COMP 206, ECSE 250, and (ECSE 343 or MATH 247) or equivalents.
        ---OUTPUT---
        ['&', 'ECSE 205', 'COMP 206', 'ECSE 250', ['|', 'ECSE 343', 'MATH 247']]

        ---INPUT---
        Prerequisites: MATH 202 or (MATH 250 and MATH 206)
        ---OUTPUT---
        ['|', 'MATH 202', ['&', 'MATH 250', 'MATH 206']]

        ---INPUT---
        Prerequisites: Any of two in the following: MATH 202, MATH 250, MATH 333 or permission of instructor
        ---OUTPUT---
        ['|', ['&', 'MATH 202', 'MATH 250'], ['&', 'MATH 250', 'MATH 333'], ['&', 'MATH 202', 'MATH 333']]
        """
        )

        for i, (req, label) in enumerate(zip(reqs, expected)):
            try:
                prediction = self.prompt([extended_prompt + "\n" + req])
                print("Predicted: ", prediction)
                print("Actual: ", label)
                print(f"({i}/{len(reqs)})")
                prediction = prediction.replace("\n", "")
                predictions.append(prediction)
            except Exception as e:
                print(f"error: {e}")
                predictions.append("")
                continue

        out = {"index": dataset["index"], "predictions": predictions}
        df = pd.DataFrame(out)
        df.to_csv(os.path.join("results", "gemini-few-shot.csv"), index=False)


if __name__ == "__main__":
    load_dotenv()

    model = Model.initialize()

    test_data_path = os.path.join("dataset", "test.csv")
    test_set = pd.read_csv(test_data_path)

    print(model.zero_shot(test_set))
    # print(model.one_shot(test_set))
