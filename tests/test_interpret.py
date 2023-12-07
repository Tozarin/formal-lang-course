import pytest

from project.interpret.visitor import InterpretVisitor
from project.interpret.interpret import interpret
from project.interpret.parser import parse
from common_info import interpret_test


def test_interpret():
    for code, expected in interpret_test:
        visitor = InterpretVisitor()
        visitor.is_print = False
        assert visitor.visitPrint(parse(code)) == expected
