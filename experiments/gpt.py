from openai import OpenAI
import pandas as pd
import os
import json
import tiktoken
import dotenv

# --- Utils ---

# TODO: Refine the prompt
PROMPT = "Given a list of course requirements, parse it into a logic expression tree structure. Each node is represented by an array or a string. Non-leaf nodes are arrays, and represent nodes for logical operators. The first element in the array is a logical operator (AND represented by '&', OR being represented by '|'), the rest of the elements in the array are the children. Leaf nodes are strings, not arrays, and their values are the courses in the requirements. These are only allowed to be valid course codes, not any arbitrary string. A valid course code is 4 uppercase/numeric characters followed by a 3 digit number."


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


def zero_shot(client: OpenAI, dataset: pd.DataFrame):
    reqs = dataset["requisite"]
    expected = dataset["object_tree"]

    for req, label in zip(reqs, expected):
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": req},
            ],
            temperature=0,
        )
        prediction = completion.choices[0].message.content
        print("Predicted: ", prediction)
        print("Actual: ", label)


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

    # WARNING: Uncommenting this will create a new finetune job
    # client.files.create(file=open(message_data_path, "rb"), purpose="fine-tune")
    # client.fine_tuning.jobs.create(
    #     training_file=train_data_path, model="gpt-3.5-turbo-1106"
    # )

    zero_shot(client, test_set)


if __name__ == "__main__":
    main()
