import pytest

from copy import deepcopy

from project.grammar.recursive_state_machines import (
    recursive_state_machine_from_extended_contex_free_grammar,
    minimize_recursive_state_machine,
    build_binary_matrix_by_rsm,
)
from project.grammar.extended_contex_free_grammar import (
    extend_contex_free_grammar,
    extended_contex_free_grammar_from_string,
)
from common_info import (
    path_to_grammars,
    extended_grammars,
    common_starting_symbol,
    build_binary_matrix_rsm,
)


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


def test_build_binary_matrix_by_rsm():

    for string_grammar, expected_states, expected_matrix in build_binary_matrix_rsm:
        grammar = extended_contex_free_grammar_from_string(
            string_grammar, common_starting_symbol
        )
        recursive_state_machine = (
            recursive_state_machine_from_extended_contex_free_grammar(
                grammar, common_starting_symbol
            )
        )
        binary_matrix = build_binary_matrix_by_rsm(recursive_state_machine)

        assert len(binary_matrix.states) == len(expected_states)
        for index, state in enumerate(binary_matrix.states):
            expected = expected_states[index]
            assert (state.value[0].value, state.value[1]) == expected[0]
            assert state.is_start == expected[1]
            assert state.is_final == expected[2]

        assert binary_matrix.matrix.keys() == expected_matrix.keys()
        for key in binary_matrix.matrix.keys():
            result = []
            matrix = binary_matrix.matrix[key].nonzero()
            for index in range(len(matrix[0])):
                result.append([matrix[0][index], matrix[1][index]])

            assert result == expected_matrix[key]
