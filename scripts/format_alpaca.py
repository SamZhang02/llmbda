# Formats the dataset to the Stanford-Alpaca format

import argparse
import pandas as pd 
import sys

def format_to_alpaca(requisite, tree):
    text = f"###User:\n{requisite}\n\n###Answer:\n{tree}"
    return text 


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset')
    parser.add_argument('outpath')

    args = parser.parse_args()

    dataset_path = args.dataset

    try:
        df = pd.read_csv(dataset_path)
    except Exception as e:
        print(f"Unable to read dataset at {dataset_path}, error: {e}", file=sys.stderr)
        exit(1)

    indices = df["index"].to_list()
    requisites = df["requisite"].to_list()
    object_trees = df["object_tree"].to_list()

    formatted_instructions = [format_to_alpaca(req_to_tree[0], req_to_tree[1]) for req_to_tree in zip(requisites, object_trees)]

    formatted_df = pd.DataFrame({
        "index":indices, 
        "instruction": formatted_instructions
    })

    try:
        formatted_df.to_csv(args.outpath) 
    except Exception as e:
        print(f"Unable to save dataset csv at {args.outpath}, error: {e}", file=sys.stderr)
        exit(1)
