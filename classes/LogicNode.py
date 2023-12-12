from __future__ import annotations
from typing import List, Dict
from functools import reduce

class LogicNode:

    def __init__(self, value:str | List) -> None:
        """Initialize a node with a list or a string; 
        Recursively points to its children if given a list"""

        if type(value) is str:
            self.value = value
            self.children = list()
            self.is_leaf = True
        else: 
            self.value = value[0]
            self.children = [LogicNode(child) for child in value[1:]]
            self.is_leaf = False


    def get_children(self) -> List[LogicNode]:
        return self.children

    def get_value(self) -> str:
        return self.value

    def _get_leaves(self) -> List[str]:

        if self.is_leaf:
            return [self.value]

        return reduce(lambda a,b: a + b, [child._get_leaves() for child in self.children])
    
    def _get_height(self) -> int:

        if self.is_leaf:
            return 1
        return 1 + max([child._get_height() for child in self.children])


    def __str__(self) -> str:
        """Prints the node and its children for debugging, J
        with bracket syntax similar to Lisp"""

        if not self.children:
            return f"({self.value})"

        return "(" + self.value + f" {reduce(lambda a,b: a+ ' ' + b, [child.__str__() for child in self.children])}" + ")"

    def _get_coursecodes(self) -> List[str]:
        if self.is_leaf:
            return [self.value]

        return list(reduce(lambda a,b : a+b, [child._get_coursecodes() for child in self.children]))

    def _compute_truth(self, rules:Dict[str, bool]) -> bool:
        """Given a syntax tree node with course codes replaced to booleans, 
        compute whether the logical proposition is true of false based on its subtrees.
        """

        if self.is_leaf:
            return rules[self.value]

        if self.value == "&":
            return reduce(lambda a, b: a and b, [child._compute_truth(rules) for child in self.children])
        else:
            return reduce(lambda a, b: a or b, [child._compute_truth(rules) for child in self.children])

if __name__ == "__main__":
    node = LogicNode(["&", "COMP 202", ["|", "COMP 250", "COMP 206"]])


