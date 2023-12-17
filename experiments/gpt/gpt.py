import json
import os

import dotenv
import pandas as pd
import tiktoken
from openai import OpenAI
from typing import Literal

# --- Utils ---

PROMPT = "Given a list of course requirements, parse it into a logic expression tree structure. Each node is represented by an string or array. Non-leaf nodes are arrays, and represent nodes for logical operators. The first element in the array is a logical operator (AND represented by '&', OR being represented by '|'), the rest of the elements in the array are the children. Logical expressions should only ever be in the first element of the array. Every non-leaf node should have at least two children. Leaf nodes are strings, never arrays. Leaf node values are the course codes in the requirements. These are only allowed to be valid course codes, not any arbitrary string. As such, you should ignore things like 'equivalent' or 'permission of instructor'. A valid course code is 4 uppercase/numeric characters followed by a space, then a 3 digit number. Use single quotes for strings. Do not give any explanation, just output the parsed data."


def get_json_message_data(file: str):
    data = pd.read_csv(file)
    reqs = data["requisite"].to_list()
    expected = data["object_tree"].to_list()
    training_examples = []

    for req, ans in zip(reqs, expected):
        training_examples.append(
            {
                "messages": [
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": req},
                    {"role": "assistant", "content": ans},
                ]
            }
        )

    total_tokens = sum(
        num_tokens_from_messages(m["messages"]) for m in training_examples
    )
    print("Total tokens for finetune data: ", total_tokens)

    return training_examples


def num_tokens_from_messages(messages):
    tokens_per_message = 3
    num_tokens = 0
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-1106")

    for message in messages:
        num_tokens += tokens_per_message
        num_tokens += len(encoding.encode(message["content"]))

    return num_tokens


# def finetune(client: OpenAI, train_data_path: str):
#     client.files.create(file=open(train_data_path, "rb"), purpose="fine-tune")
#     client.fine_tuning.jobs.create(
#         training_file=train_data_path, model="gpt-3.5-turbo-1106"
#     )


# --- Experiments ---


def zero_shot(
    client: OpenAI,
    dataset: pd.DataFrame,
    model: Literal["gpt-3.5-turbo-1106", "gpt-4-1106-preview"] = "gpt-3.5-turbo-1106",
):
    reqs = dataset["requisite"]
    expected = dataset["object_tree"]

    predictions = []

    for i, (req, label) in enumerate(zip(reqs, expected)):
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": req},
            ],
            temperature=0,
        )
        prediction = completion.choices[0].message.content
        if prediction is None:
            raise ValueError("GPT gave none for message content")

        print("Predicted: ", prediction)
        print("Actual: ", label)
        print(f"({i}/{len(reqs)})")
        prediction = prediction.replace("\n", "")
        predictions.append(prediction)

    out = {"index": dataset["index"], "predictions": predictions}
    df = pd.DataFrame(out)
    df.to_csv(os.path.join("results", f"{model}-zero-shot.csv"), index=False)


def few_shot(
    client: OpenAI,
    dataset: pd.DataFrame,
    model: Literal["gpt-3.5-turbo-1106", "gpt-4-1106-preview"] = "gpt-3.5-turbo-1106",
):
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
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": extended_prompt},
                {"role": "user", "content": req},
            ],
            temperature=0,
        )
        prediction = completion.choices[0].message.content
        if prediction is None:
            raise ValueError("GPT gave none for message content")
        print("Predicted: ", prediction)
        print("Actual: ", label)

        print(f"({i}/{len(reqs)})")
        prediction = prediction.replace("\n", "")
        predictions.append(prediction)

    out = {"index": dataset["index"], "predictions": predictions}
    df = pd.DataFrame(out)
    df.to_csv(os.path.join("results", f"{model}-few-shot.csv"), index=False)


def finetuned(client: OpenAI, dataset: pd.DataFrame):
    model_name = os.environ.get("FINETUNE_MODEL_NAME")
    if model_name is None:
        print("Finetune model name not present in environment variables, skipping.")
        return

    reqs = dataset["requisite"]
    expected = dataset["object_tree"]

    predictions = []

    for i, (req, label) in enumerate(zip(reqs, expected)):
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": req},
            ],
            temperature=0,
        )
        prediction = completion.choices[0].message.content
        if prediction is None:
            raise ValueError("GPT gave none for message content")

        print("Predicted: ", prediction)
        print("Actual: ", label)
        print(f"({i}/{len(reqs)})")
        prediction = prediction.replace("\n", "")
        predictions.append(prediction)

    out = {"index": dataset["index"], "predictions": predictions}
    df = pd.DataFrame(out)
    df.to_csv(os.path.join("results", "gpt3.5-finetuned.csv"), index=False)


def main():
    dotenv.load_dotenv()

    # Create jsonl file for fine-tuning
    train_data_path = os.path.join("dataset", "train.csv")
    message_data_path = os.path.join("dataset", "train.jsonl")

    data = get_json_message_data(train_data_path)
    with open(message_data_path, "w+") as f:
        f.write("\n".join(map(json.dumps, data)))

    test_data_path = os.path.join("dataset", "test.csv")
    test_set = pd.read_csv(test_data_path)

    client = OpenAI()

    # zero_shot(client, test_set, model="gpt-4-1106-preview")
    few_shot(client, test_set, model="gpt-4-1106-preview")
    # few_shot(client, test_set)


if __name__ == "__main__":
    main()
