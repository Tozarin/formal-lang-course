import pytest

from pyformlang.cfg import Variable
from pyformlang.regular_expression import Regex

from project.grammar.extended_contex_free_grammar import (
    extend_contex_free_grammar,
    extended_contex_free_grammar_from_string,
    extended_contex_free_grammar_from_file,
)
from project.utils.grammar_utils import read_contex_free_grammar_from_file
from common_info import (
    path_to_grammars,
    names_of_grammar_files,
    extended_grammars,
    common_starting_symbol,
)


def test_extend_contex_free_grammar():

    for names_of_grammar_file, starting_symbol, _, _ in names_of_grammar_files:
        contex_free_grammar = read_contex_free_grammar_from_file(
            path_to_grammars + names_of_grammar_file, starting_symbol
        )
        extended_contex_free_grammar = extend_contex_free_grammar(
            contex_free_grammar, starting_symbol
        )

        assert (
            extended_contex_free_grammar.starting_symbol
            == contex_free_grammar.start_symbol
        )
        assert (
            extended_contex_free_grammar.nonterminals == contex_free_grammar.variables
        )
        assert extended_contex_free_grammar.terminals == contex_free_grammar.terminals


def test_extended_contex_free_grammar_from_string():

    for (
        string_extended_contex_free_grammar,
        expected_nonterminals,
        expected_terminals,
        expected_productions,
    ) in extended_grammars:
        extended_contex_free_grammar = extended_contex_free_grammar_from_string(
            string_extended_contex_free_grammar, common_starting_symbol
        )

        assert set(extended_contex_free_grammar.nonterminals) == set(
            map(lambda char: Variable(char), expected_nonterminals)
        )
        assert set(extended_contex_free_grammar.terminals) == set(
            map(lambda char: Variable(char), expected_terminals)
        )
        assert extended_contex_free_grammar.starting_symbol == common_starting_symbol
