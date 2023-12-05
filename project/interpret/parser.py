from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker, ParserRuleContext, TerminalNode
from pydot import Dot, Node, Edge

from project.interpret.LenguageLexer import LenguageLexer
from project.interpret.LenguageParser import LenguageParser
from project.interpret.LenguageListener import LenguageListener


def parse(code: str) -> LenguageParser:

    return LenguageParser(CommonTokenStream(LenguageLexer(InputStream(code))))

def check_correctness(code: str) -> bool:

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

    ast = parser.programm()
    if parser.getNumberOfSyntaxErrors() > 0:
        raise ValueError("Parser has syntax errors")

    if not listener.dot.write(path):
        raise RuntimeError("Cant save tree")

class CorrectTreeListener(LenguageListener):

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

    def __init__(self):
        self.dot = Dot("code", strict=True)
        self.curr = 0
        self.stack = []

    def enterEveryRule(self, contex: ParserRuleContext):
        self.dot.add_node(Node(self.curr, label=LenguageParser.ruleNames[contex.getRuleIndex()]))

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