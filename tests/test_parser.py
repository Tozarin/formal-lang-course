import pytest

from project.interpret.parser import parse, check_correctness, save_to_dot
from common_info import (
    parser_test_true,
    parser_test_false,
    parser_dot_test,
    parser_dot_test_example,
    path_to_results,
)


def test_check_correctness():
    for code in parser_test_true:
        assert check_correctness(code)

    for code in parser_test_false:
        assert not check_correctness(code)


def test_save_to_dot():
    path = path_to_results + "ast_test.dot"
    parser = parse(parser_dot_test)
    save_to_dot(parser, path)

    with open(path_to_results + parser_dot_test_example, "r") as file:
        example = file.read()

    with open(path, "r") as file:
        writed = file.read()
        assert writed == example
