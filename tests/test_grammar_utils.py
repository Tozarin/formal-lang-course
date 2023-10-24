from pyformlang.cfg import CFG, Variable

from project.utils.grammar_utils import (
    contex_free_to_weak_chomsky_form,
    read_contex_free_grammar_from_file,
)
from common_info import (
    path_to_grammars,
    contex_free_and_weak_chomsky_forms,
    names_of_grammar_files,
)


def test_contex_free_to_weak_chomsky_form():

    for (
        contex_free_form,
        contex_free_form_starting_nonterminal,
        expected_grammar,
        expected_grammar_starting_symbol,
    ) in contex_free_and_weak_chomsky_forms:
        weak_chomsky_form = contex_free_to_weak_chomsky_form(
            contex_free_form, contex_free_form_starting_nonterminal
        )
        expected_grammar = CFG.from_text(
            expected_grammar, Variable(expected_grammar_starting_symbol)
        )

        assert weak_chomsky_form.start_symbol == expected_grammar.start_symbol
        assert weak_chomsky_form.productions == expected_grammar.productions


def test_read_contex_free_grammar_from_file():

    for (
        name_of_file,
        starting_symbol,
        expected_grammar,
        expected_starting_symbol,
    ) in names_of_grammar_files:
        expected_grammar = CFG.from_text(
            expected_grammar, Variable(expected_starting_symbol)
        )
        contex_free_grammar = read_contex_free_grammar_from_file(
            path_to_grammars + name_of_file, starting_symbol
        )

        assert contex_free_grammar.start_symbol == expected_grammar.start_symbol
        assert contex_free_grammar.productions == expected_grammar.productions
