# Requires huggingface's transformer API, with an account that has access to llama models 

import pandas as pd
import argparse

from transformers import AutoTokenizer
import transformers 
import torch
torch.device('cuda')

# - Util

def load_data(path):
    data = pd.read_csv(path)

    return data[["index", "requisite"]]


prompt = """Given a string of course requirement, parse it into a logic expression tree structure. Each node is represented by either a string or a python array. 
    Non-leaf nodes are arrays, and represent nodes for logical operators. The first element in the array is a logical operator (AND represented by '&', OR being represented by '|'), 
    the rest of the elements in the array are the children. Logical expressions should only ever be in the first element of the array. 
    Leaf nodes are strings, never arrays. Leaf node values are the course codes in the requirements. 

    return These are only allowed to be valid course codes, not any arbitrary string. 
    A valid course code is 4 uppercase/numeric characters followed by a space, then a 3 digit number and optionally 2 uppercase/numeric characters. 
    Use single quotes for strings.

    For any non course code requirements, ignore them in your output.

    Below are some examples of conversations to help you form your output, where each example is within triple backticks:

    User: COMP 202
    Assistant: 'COMP 202'

    User: COMP 202, COMP 250
    Assistant: ['&', 'COMP 202', 'COMP 250']

    User: COMP 202 and (COMP 250 or COMP 206 or any 200 level COMP course) 
    Assistant: ['&', 'COMP 202', ['|', 'COMP 250', 'COMP 206']]

    User: MATH 202 or (MATH 250 and MATH 206)
    Assistant: ['|', 'MATH 202', ['&', 'MATH 250', 'MATH 206']]

    User: Any of two in the following: MATH 202, MATH 250, MATH 333 or permission of instructor
    Assistant: ['|', ['&', 'MATH 202', 'MATH 250'], ['&', 'MATH 250', 'MATH 333'], ['&', 'MATH 202', 'MATH 333']]

    Only output the tree representationm, do not output anything else, do not give an explanation, do not write it within triple backticks.
    """


def test(input: str) -> str:
    print(f"predicting {input}")

    try:
        sequences = pipeline(
            f" <s>[INST] <<SYS>>\n{prompt}<</SYS>>\n\nConvert the following string into a structured logic expression tree: {input}[/INST]",
            do_sample=True,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id,
            max_length=1000,
        )

        print(f"prediction success: {sequences[0]['generated_text']}" if sequences else "prediction failed: empty sequence")
        return "Result: " + sequences[0]['generated_text'] if sequences else ""

    except Exception as e: 
        print(f"prediction failed: {e}")
        return ""

# - Experiments

parser = argparse.ArgumentParser()

parser.add_argument('--path')    
parser.add_argument('--model')    

args = parser.parse_args()

test_data_path = "../../dataset/test.csv" if not args.path else args.path
model = "meta-llama/Llama-2-7b-chat-hf" if not args.model else args.model

tokenizer = AutoTokenizer.from_pretrained(model)

pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    torch_dtype=torch.float16,
    device_map="auto",
)

data = load_data(test_data_path)

indices = data["index"].to_list()
requisites = data["requisite"].to_list()

pred = [test(req) for req in requisites]

pred_df = pd.DataFrame({
    "index": indices,
    "prediction": pred
})

pred_df.to_csv("./llama2_chat_pred.csv")
