from antlr4 import (
    InputStream,
    CommonTokenStream,
    ParseTreeWalker,
    ParserRuleContext,
    TerminalNode,
)
from pydot import Dot, Node, Edge

from project.interpret.LenguageLexer import LenguageLexer
from project.interpret.LenguageParser import LenguageParser
from project.interpret.LenguageListener import LenguageListener


def parse(code: str) -> LenguageParser:

    """
    From given code that presented as string creates anltr parser

    Args:
        code: code of programm in string

    Returns:
        Antlr parser
    """

    return LenguageParser(CommonTokenStream(LenguageLexer(InputStream(code))))


def check_correctness(code: str) -> bool:

    """
    Cheks that given code is subset of original language

    Args:
        code: code of programm in string

    Returns:
        Bool value: subset of not subset
    """

    parser = parse(code)
    parser.removeErrorListeners()
    ast = parser.programm()

    listener = CorrectTreeListener()

    walker = ParseTreeWalker()
    correct_flag = True
    try:
        walker.walk(listener, ast)
    except ValueError:
        correct_flag = False

    return parser.getNumberOfSyntaxErrors() == 0 and correct_flag


def save_to_dot(parser: LenguageParser, path: str):

    """
    Saves given parsed code as parsing tree in dot file at path

    Args:
        parser: antlr parser with parsed code
        path: path to file where tree will be saved

    Returns:
        Nothing
    """

    ast = parser.programm()
    if parser.getNumberOfSyntaxErrors() > 0:
        raise ValueError("Parser has syntax errors")

    listener = DotTreeListener()
    walker = ParseTreeWalker()
    walker.walk(listener, ast)

    if not listener.dot.write(path):
        raise RuntimeError("Cant save tree")


class CorrectTreeListener(LenguageListener):

    """
    Inner code class to checks correction of code

    Args:
        has_sub: flag for inner functions
    """

    def __init__(self):
        self.has_sub = False

    def enterEveryRule(self, contex: ParserRuleContext):
        self.has_sub = False

    def exitEveryRule(self, contex: ParserRuleContext):
        if not self.has_sub:
            raise ValueError("Parser has syntax errors")

        self.has_sub = True

    def visitTerminal(self, node: TerminalNode):
        self.has_sub = True


class DotTreeListener(LenguageListener):

    """
    Inner code class to save_to_dot function

    Args:
        dot: parsing tree as dot
        curr: current working node
        stack: stack of ordered nodes
    """

    def __init__(self):
        self.dot = Dot("code", strict=True)
        self.curr = 0
        self.stack = []

    def enterEveryRule(self, contex: ParserRuleContext):
        self.dot.add_node(
            Node(self.curr, label=LenguageParser.ruleNames[contex.getRuleIndex()])
        )

        if len(self.stack) > 0:
            self.dot.add_edge(Edge(self.stack[-1], self.curr))
        self.stack.append(self.curr)
        self.curr += 1

    def exitEveryRule(self, contex: ParserRuleContext):
        self.stack.pop()

    def visitTerminal(self, node: TerminalNode):
        self.dot.add_node(Node(self.curr, label=f"'{node}'", shape="box"))
        self.dot.add_edge(Edge(self.stack[-1], self.curr))
        self.curr += 1
