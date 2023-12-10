from __future__ import annotations
from LogicNode import LogicNode
from typing import List,Dict
from itertools import product
from enum import Enum
import re 

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
    def is_well_formed(lst:List) -> bool:
        """
        Method to check if a list if a well formed logic tree
        """
        return True

    @classmethod
    def from_list(cls, lst:List) -> LogicTree:
        """
        Instantiate a tree from a list
        """
        if not cls.is_well_formed(lst):
            raise NotWellFormedTree(f"{lst} is not a well formed tree")

        return cls(LogicNode(lst), lst)

    def get_coursecodes(self) -> List[str]:
        return self.root._get_coursecodes()

    def compute_truth(self, rules:Dict[str,bool]) -> bool:
        """Given a logic tree, compute whether the logical proposition is true of false based on a set of rules."""
        return self.root._compute_truth(rules)

    def equals(self, other:LogicTree) -> bool:
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

    def complexity(self) -> TreeComplexity:
        """
        Method to compute the complexity of a tree, returns an enum
        """

        number_of_courses = len(set(self.get_coursecodes()))

        if number_of_courses < 3:
            return TreeComplexity.TRIVIAL

        elif number_of_courses < 5:
            return TreeComplexity.MEDIUM

        else:
            return TreeComplexity.HARD

    def distance_to(self,other:LogicTree) -> int:
        """
        Method to compute the edit distance of two trees
        """
        ...


if __name__ == "__main__":
    tree1 = LogicTree.from_list(["&", "COMP 202", ["|", "COMP 250", "COMP 206"]])
    tree2 = LogicTree.from_list(["&", "COMP 202", ["&", "COMP 250", "COMP 206"]])
    tree3 = LogicTree.from_list(["|", ["&", "COMP 202", "COMP 250"], ["&", "COMP 202", "COMP 206"]])
    tree4 = LogicTree.from_list(["|", ["&", "COMP 302", "COMP 250"], ["&", "COMP 202", "COMP 206"]])

    print(tree1.equals(tree2))
    print(tree1.equals(tree3))
    print(tree2.equals(tree3))
    print(tree3.equals(tree4))



