import pytest

from copy import deepcopy

from project.grammar.recursive_state_machines import (
    recursive_state_machine_from_extended_contex_free_grammar,
    minimize_recursive_state_machine,
)
from project.grammar.extended_contex_free_grammar import (
    extend_contex_free_grammar,
    extended_contex_free_grammar_from_string,
)
from common_info import extended_grammars, common_starting_symbol


def test_recursive_state_machine_from_extended_contex_free_grammar():

    for (
        string_extended_contex_free_grammar,
        expected_nonterminals,
        expected_terminals,
        expected_productions,
    ) in extended_grammars:
        extended_contex_free_grammar = extended_contex_free_grammar_from_string(
            string_extended_contex_free_grammar, common_starting_symbol
        )
        recursive_state_machine = (
            recursive_state_machine_from_extended_contex_free_grammar(
                extended_contex_free_grammar, common_starting_symbol
            )
        )

        assert (
            recursive_state_machine.starting_symbol
            == extended_contex_free_grammar.starting_symbol
        )
        assert len(recursive_state_machine.subautomatons) == len(
            extended_contex_free_grammar.productions
        )


def test_minimize_recursive_state_machine():

    for (
        string_extended_contex_free_grammar,
        expected_nonterminals,
        expected_terminals,
        expected_productions,
    ) in extended_grammars:
        recursive_state_machine = (
            recursive_state_machine_from_extended_contex_free_grammar(
                string_extended_contex_free_grammar, common_starting_symbol
            )
        )
        minimized_recursive_state_machine = minimize_recursive_state_machine(
            deepcopy(recursive_state_machine)
        )

        assert len(minimized_recursive_state_machine.subautomatons) == len(
            recursive_state_machine.subautomatons
        )

        for nonterminal in recursive_state_machine.subautomatons:
            assert minimized_recursive_state_machine.subautomatons[
                nonterminal
            ].is_equivalent_to(recursive_state_machine.subautomatons[nonterminal])
