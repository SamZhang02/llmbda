import sys
import os

# weird python fuckery to import LogicTree
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ast
import argparse
import pandas as pd
from pathlib import Path
from typing import List, Dict
from classes.LogicTree import LogicTree, NotWellFormedTree,NotWellFormedTree, TreeComplexity

def get_num_complexities(ans:List[str], complexity:TreeComplexity) -> int:
    return len([s for s in ans if LogicTree.from_list(ast.literal_eval(s)).complexity() == complexity])


def eval(ans:List[str], pred:List[str]) -> Dict:
    """
    Takes in the human labeled column and the pred column,
    compute and return the the two columns' accuracy, avg tree sim, percentage well-formedness
    """

    num_samples = len(ans)
    num_logically_equivalent = 0
    num_well_formed_trees = 0
    tree_sim_sum = 0

    num_trivial = get_num_complexities(ans, TreeComplexity.TRIVIAL)
    num_logically_equivalent_trivial = 0
    num_well_formed_trees_trivial = 0
    tree_sim_sum_trivial = 0

    num_medium = get_num_complexities(ans, TreeComplexity.MEDIUM)
    num_logically_equivalent_medium = 0
    num_well_formed_trees_medium = 0
    tree_sim_sum_medium = 0

    num_hard = get_num_complexities(ans, TreeComplexity.HARD)
    num_logically_equivalent_hard = 0
    num_well_formed_trees_hard = 0
    tree_sim_sum_hard = 0

    for ans_string, pred_string in zip(ans,pred):
        try:
            pred_lst = ast.literal_eval(pred_string)
        except:
            continue

        try:
            pred_tree = LogicTree.from_list(pred_lst)
        except NotWellFormedTree:
            continue

        ans_tree = LogicTree.from_list(ast.literal_eval(ans_string))

        num_well_formed_trees += 1
        match ans_tree.complexity():
            case TreeComplexity.TRIVIAL:
                num_well_formed_trees_trivial += 1
                num_logically_equivalent_trivial += 1 if ans_tree == pred_tree else 0
                tree_sim_sum_trivial += ans_tree.distance_to(pred_tree)

            case TreeComplexity.MEDIUM:
                num_well_formed_trees_medium += 1
                num_logically_equivalent_medium += 1 if ans_tree == pred_tree else 0
                tree_sim_sum_medium += ans_tree.distance_to(pred_tree)

            case TreeComplexity.HARD:
                num_well_formed_trees_hard += 1
                num_logically_equivalent_hard += 1 if ans_tree == pred_tree else 0
                tree_sim_sum_hard += ans_tree.distance_to(pred_tree)

        num_logically_equivalent += 1 if ans_tree == pred_tree else 0
        tree_sim_sum += ans_tree.distance_to(pred_tree)

    accuracy =  num_logically_equivalent / num_samples
    avg_sim = tree_sim_sum / num_samples
    well_formed_percent = num_well_formed_trees / num_samples

    accuracy_trivial =  num_logically_equivalent_trivial / num_trivial
    avg_sim_trivial = tree_sim_sum_trivial / num_trivial
    well_formed_percent_trivial = num_well_formed_trees_trivial / num_trivial

    accuracy_medium =  num_logically_equivalent_medium / num_medium
    avg_sim_medium = tree_sim_sum_medium / num_medium
    well_formed_percent_medium = num_well_formed_trees_medium / num_medium

    accuracy_hard =  num_logically_equivalent_hard / num_hard
    avg_sim_hard = tree_sim_sum_hard / num_hard
    well_formed_percent_hard = num_well_formed_trees_hard / num_hard

    return {
        "accuracy": accuracy,
        "avg_tree_edit_distance": avg_sim,
        "well-formedness": well_formed_percent,
        TreeComplexity.TRIVIAL: {
            "accuracy": accuracy_trivial,
            "avg_tree_edit_distance": avg_sim_trivial,
            "well-formedness": well_formed_percent_trivial,
        },
        TreeComplexity.MEDIUM: {
            "accuracy": accuracy_medium,
            "avg_tree_edit_distance": avg_sim_medium,
            "well-formedness": well_formed_percent_medium,
        },
        TreeComplexity.HARD : {
            "accuracy": accuracy_hard,
            "avg_tree_edit_distance": avg_sim_hard,
            "well-formedness": well_formed_percent_hard,
        }
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_name")
    parser.add_argument("ans_path", default="./dataset/test.csv")
    parser.add_argument("pred_path")
    parser.add_argument("--log_result", default="")
    parser.add_argument("--ans_text_field", default='object_tree')
    parser.add_argument("--pred_text_field", default='predictions')
    parser.add_argument("--join_on", default='index')

    args = parser.parse_args()

    ans_df = pd.read_csv(args.ans_path)
    pred_df = pd.read_csv(args.pred_path)

    all_df = pd.merge(ans_df, pred_df, how="left", on="index")

    indices = all_df[args.join_on]
    ans = all_df[args.ans_text_field]
    predictions = all_df[args.pred_text_field]

    if predictions.isna().any():
        raise Exception(f"Some columns were not joined {predictions.isna().any()}, did you forget an inference?")

    results = eval(ans.to_list(), predictions.to_list())

    output = f"""
    ----- OVERALL -----
    ACCURACY: {results['accuracy']}
    AVERAGE TREE EDIT DISTANCE: {results['avg_tree_edit_distance']}
    PERCENT WELL-FORMED TREES: {results['well-formedness']}

    ----- TRIVIAL -----
    ACCURACY: {results[TreeComplexity.TRIVIAL]['accuracy']}
    AVERAGE TREE EDIT DISTANCE: {results[TreeComplexity.TRIVIAL]['avg_tree_edit_distance']}
    PERCENT WELL-FORMED TREES: {results[TreeComplexity.TRIVIAL]['well-formedness']}

    ----- MEDIUM -----
    ACCURACY: {results[TreeComplexity.MEDIUM]['accuracy']}
    AVERAGE TREE EDIT DISTANCE: {results[TreeComplexity.MEDIUM]['avg_tree_edit_distance']}
    PERCENT WELL-FORMED TREES: {results[TreeComplexity.MEDIUM]['well-formedness']}

    ----- HARD -----
    ACCURACY: {results[TreeComplexity.HARD]['accuracy']}
    AVERAGE TREE EDIT DISTANCE: {results[TreeComplexity.HARD]['avg_tree_edit_distance']}
    PERCENT WELL-FORMED TREES: {results[TreeComplexity.HARD]['well-formedness']}
    """

    print(f"Results:{output}")

    if args.log_result:
        outpath = Path(args.log_result)
        outpath.parent.mkdir(exist_ok=True, parents=True)
        with open(outpath, "w") as fobj:
            fobj.write(output)
