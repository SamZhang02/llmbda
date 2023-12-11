from __future__ import annotations
from LogicNode import LogicNode
from typing import List,Dict
from itertools import product
from enum import Enum
import re 
import zss

COURSE_CODE_PATTERN = re.compile(r"([A-Z0-9]{4} [0-9]{3}(?:D1|D2|N1|N2|J1|J2|J3)?)")

class TreeComplexity(Enum):
    TRIVIAL = 1
    MEDIUM = 2
    HARD = 3

class NotWellFormedTree(Exception): pass

class LogicTree:

    def __init__(self, root:LogicNode, lst:List):
        self.root = root
        self.lst = lst

    @staticmethod
    def is_well_formed(entity:List | str) -> bool:
        """
        Method to check if a list if is a well formed logic tree before trying to 
        instantiate it as the class.
        """

        match entity:
            case str():
                m = COURSE_CODE_PATTERN.fullmatch(entity)
                if m is None:
                    print(f"Invalid course code {entity}")

                return m is not None
            case list():
                if entity[0] not in ["&", "|"]:
                    print(f"Invalid operator {entity[0]}")
                    return False

                if len(entity) < 3:
                    print("Tree node must have at least 2 children")
                    return False

                return all([LogicTree.is_well_formed(child) for child in entity[1:]])

    @classmethod
    def from_list(cls, lst:List) -> LogicTree:
        """
        Instantiate a tree from a list
        """
        if not cls.is_well_formed(lst):
            raise NotWellFormedTree(f"Cannot instantiate LogicTreee, {lst} is not a well formed tree")

        return cls(LogicNode(lst), lst)

    def get_coursecodes(self) -> List[str]:
        return self.root._get_coursecodes()

    def compute_truth(self, rules:Dict[str,bool]) -> bool:
        """Given a logic tree, compute whether the logical proposition is true of false based on a set of rules."""
        return self.root._compute_truth(rules)

    def __eq__(self, other:LogicTree) -> bool:
        """Given two logic trees, compute whether they are logically equivalent."""
        self_course_codes = set(self.get_coursecodes())
        other_course_codes = set(other.get_coursecodes())

        if self_course_codes != other_course_codes:
            return False

        number_of_courses = len(self_course_codes)
        all_rules_permutations = product([True, False], repeat=number_of_courses)

        for perm in all_rules_permutations:
            rules = {k:v for k,v in zip(self_course_codes, perm)}
            if self.compute_truth(rules) != other.compute_truth(rules):
                return False

        return True

    def get_leaves(self) -> List[str]:
        return self.root._get_leaves()

    def get_height(self) -> int:
        return self.root._get_height()

    def complexity(self) -> TreeComplexity:
        """
        Method to compute the complexity of a tree, scales with number of leaves and tree height.
        """

        number_of_leaves = len(self.get_leaves())
        height = self.get_height()

        complexity_score = (number_of_leaves * height-1)

        if complexity_score <= 4:
            return TreeComplexity.TRIVIAL

        elif complexity_score <= 15:
            return TreeComplexity.MEDIUM

        else:
            return TreeComplexity.HARD


    def distance_to(self,other:LogicTree, return_operations=False) -> int:
        """
        Method to compute the edit distance of two trees
        """
        return zss.simple_distance(self.root, other.root, 
                                   get_children=LogicNode.get_children, 
                                   get_label=LogicNode.get_value,
                                   return_operations=return_operations)


if __name__ == "__main__":
    tree1 = LogicTree.from_list(["&", "COMP 202", ["|", "COMP 250", "COMP 206"]]) 
    tree2 = LogicTree.from_list(["&", "COMP 202", ["&", "COMP 250", "COMP 206"]]) 
    tree3 = LogicTree.from_list(["|", ["&", "COMP 202", "COMP 250"], ["&", "COMP 202", "COMP 206"]]) 
    tree4 = LogicTree.from_list(["|", ["&", "COMP 302", "COMP 250"], ["&", "COMP 202", "COMP 206"]])

    assert (tree1 == tree2) is False
    assert (tree1 == tree3) is True
    assert (tree2 == tree3) is False
    assert (tree3 == tree4) is False

    assert LogicTree.is_well_formed("COMP 202") is True
    assert LogicTree.is_well_formed("hello") is False
    assert LogicTree.is_well_formed(["&", "COMP 202"]) is False
    assert LogicTree.is_well_formed(["&", "COMP 202", "COMP 250"]) is True
    assert LogicTree.is_well_formed(["&", "COMP 202J1", "COMP 250"]) is True
    assert LogicTree.is_well_formed(["&", ["|", "COMP 202", "COMP 302"], "COMP 250"]) is True

    assert tree1.distance_to(tree2) == 1
    assert tree3.distance_to(tree4) == 1
    assert tree1.distance_to(tree3) == 5

    assert sorted(tree1.get_leaves()) == sorted(["COMP 202", "COMP 250", "COMP 206"])
    assert sorted(tree3.get_leaves()) == sorted(["COMP 202", "COMP 250", "COMP 202", "COMP 206"])

    assert tree1.get_height() == 3 
    assert tree3.get_height() == 3 


