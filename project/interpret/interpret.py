from pathlib import Path

from project.interpret.visitor import InterpretVisitor
from project.interpret.parser import parse, check_correctness


def interpret(code: str):

    if not check_correctness(code):
        raise RuntimeError("Code has syntax issues")

    parser = parse(code)
    ast = parser.programm()

    visitor = InterpretVisitor()
    return visitor.visit(ast)


def from_file(path: Path):

    file = path.open()

    if not file.name.endswith(".lll"):
        raise FileNotFoundError()

    interpret("".join(file.readlines()))
