from dataclasses import dataclass, field
from functools import singledispatchmethod


@dataclass
class Node: ...


@dataclass
class GroupNode(Node):
    level: int
    nodes: list[Node] = field(default_factory=list)


    def __repr__(self) -> str:
        return f"({",".join([str(n) for n in self.nodes])})"

@dataclass
class OptionalNode(Node):
    node: Node

    def __repr__(self):
        return f"{self.node}?"

@dataclass
class LiteralNode(Node):
    value: str

    def __repr__(self):
        return f"{self.value}"

@dataclass
class AnyLiteralNode(Node):
    def __repr__(self) -> str:
        return f"."

@dataclass
class GreedyFromZeroNode(Node):
    node: Node
    def __repr__(self) -> str:
        return f"{self.node}*"

@dataclass
class GreedyFromOneNode(Node):
    node: Node
    def __repr__(self) -> str:
        return f"{self.node}+"


class RegexChecker:

    def __init__(self, graph: Node, text: str):
        self.offset = 0
        self.graph = graph
        self.text = text

    def check(self):
        try:
            valid = self._check(graph)
            return valid and self.offset == len(self.text)
        except Exception as e:
            print(f"{e!r}")
            return False

    @singledispatchmethod
    def _check(self, node: Node) -> bool:
        raise NotImplementedError

    @_check.register
    def _check_group_node(self, node: GroupNode) -> bool:
        print(node)
        valid = True
        for child in node.nodes:
            # if len(s) == 0:
            #     "String consumed too quickly"
            #     valid = False
            #     break
            valid = self._check(child)
            if not valid:
                break
        # if len(s) > 0:
        #     print("String not consumed entirely")
        #     valid = False
        return valid

    @_check.register
    def _check_optional_node(self, node: OptionalNode) -> bool:
        print(node)
        if self.offset < len(self.text):
            self._check(node.node)
        return True

    @_check.register
    def _check_literal_node(self, node: LiteralNode) -> bool:
        token = self.text[self.offset]
        print(node, token)
        valid = node.value == token
        if valid:
            self.offset += 1
        return  valid
    
    @_check.register
    def _check_any_literal_node(self, node: AnyLiteralNode) -> bool:
        token = self.text[self.offset]
        print(node, token)
        self.offset += 1
        return True
    
    @_check.register
    def _check_greedy_from_zero_node(self, node: GreedyFromZeroNode) -> bool:
        valid = True
        print(node)
        while valid and self.offset < len(self.text):
            valid = self._check(node.node)
        return True

    @_check.register
    def _check_greedy_from_one_node(self, node: GreedyFromOneNode) -> bool:
        valid = True
        counter = 0
        print(node)
        while valid and self.offset < len(self.text):
            valid = self._check(node.node)
            if valid:
                counter += 1
        return counter > 0


def parse(code: str) -> Node:
    groups_stack = []
    groups_stack.append(GroupNode(level=0))

    for token in code:
        node = None
        match token:
            case ".":
                node = AnyLiteralNode()
            # TODO: groups (()), sequences ([] with a-z, A-Z. 1-9), start enforcer (^), end enforcer ($), escape sequence (\)
            case "(":
                groups_stack.append(GroupNode(level=len(groups_stack)))
            case ")":
                node = groups_stack.pop()
            case "[":
                ...
            case "]":
                ...
            case "*":
                node = GreedyFromZeroNode(node=groups_stack[-1].nodes.pop())
            case "+":
                node = GreedyFromOneNode(node=groups_stack[-1].nodes.pop())
            case "?":
                node = OptionalNode(node=groups_stack[-1].nodes.pop())
            case _:
                node = LiteralNode(value=token)
        if node is not None:
            groups_stack[-1].nodes.append(node)
    print("------------")
    return groups_stack[-1]


if __name__ == "__main__":
    graph = parse("a(c)?")
    result = RegexChecker(graph, "ac").check()
    # TODO: add tabs for depth level when printing
    print(result)
