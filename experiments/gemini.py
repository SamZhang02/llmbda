import os
import typing as t

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv

PROMPT = """
Given a list of course requirements, parse it into a logic expression tree structure. Each node is represented by an
string or array. Non-leaf nodes are arrays, and represent nodes for logical operators. The first element in the array is
a logical operator (AND represented by '&', OR being represented by '|'), the rest of the elements in the array are the
children. Logical expressions should only ever be in the first element of the array. Leaf nodes are strings, never
arrays. Leaf node values are the course codes in the requirements. These are only allowed to be valid course codes, not
any arbitrary string. A valid course code is 4 uppercase/numeric characters followed by a space, then a 3 digit number.
Use single quotes for strings. Ignore anything words that are not valid course codes, like 'equivalent' or 'permission', etc.
Also don't write AND or OR, use & for AND and | for OR always.
"""


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
        Prerequisites: ECSE 205, COMP 206, ECSE 250, and (ECSE 343 or MATH 247) or equivalents.
        ---OUTPUT---
        ['&', 'ECSE 205', 'COMP 206', 'ECSE 250', ['|', 'ECSE 343', 'MATH 247']]
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
        df.to_csv(os.path.join("results", "gemini-one-shot.csv"), index=False)


if __name__ == "__main__":
    load_dotenv()

    model = Model.initialize()

    test_data_path = os.path.join("dataset", "test.csv")
    test_set = pd.read_csv(test_data_path)

    # print(model.zero_shot(test_set))
    print(model.one_shot(test_set))
