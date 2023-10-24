import pytest

from typing import List

from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State
from scipy.sparse import dok_matrix, lil_matrix, csr_matrix, csc_matrix

from project.utils.automata_utils import intersect_of_automata
from project.utils.bin_matrix_utils import (
    build_binary_matrix_by_nfa,
    build_nfa_by_binary_matrix,
    transitive_closure,
)
from common_info import (
    nondeterministic_automata_for_build_test,
    transitive_closure_test,
    matrix_types,
)


def build_nfa(
    transitions_list: List[tuple], starting_states: set = None, final_states: set = None
) -> NondeterministicFiniteAutomaton:

    rez = NondeterministicFiniteAutomaton()

    if not len(transitions_list):
        return rez
    else:
        rez.add_transitions(transitions_list)

    for state in starting_states:
        rez.add_start_state(State(state))
    for state in final_states:
        rez.add_final_state(State(state))

    return rez


def test_build_empty():

    for matrix_type in matrix_types:
        nfa = NondeterministicFiniteAutomaton()
        assert build_nfa_by_binary_matrix(
            build_binary_matrix_by_nfa(nfa, matrix_type)
        ).is_empty()


def test_build_from_and_to_bm():

    for (
        transitions_list,
        starting_states,
        final_states,
    ) in nondeterministic_automata_for_build_test:

        for matrix_type in matrix_types:
            original_nfa = build_nfa(transitions_list, starting_states, final_states)
            builded_nfa = build_nfa_by_binary_matrix(
                build_binary_matrix_by_nfa(original_nfa, matrix_type)
            )

            assert builded_nfa.is_equivalent_to(original_nfa)


def test_intersect_with_empty_automaton():

    for (
        transitions_list,
        starting_states,
        final_states,
    ) in nondeterministic_automata_for_build_test:

        empty_automaton = NondeterministicFiniteAutomaton()
        non_empty_automaton = build_nfa(transitions_list, starting_states, final_states)

        for matrix_type in matrix_types:
            intersect = intersect_of_automata(
                empty_automaton, non_empty_automaton, matrix_type
            )

            assert intersect.is_empty()


def test_intersect_of_automata():

    automata = [
        build_nfa(transitions_list, starting_states, final_states)
        for transitions_list, starting_states, final_states in nondeterministic_automata_for_build_test
    ]

    for left_automaton in automata:
        for right_automaton in automata:
            expected_automaton = left_automaton.get_intersection(right_automaton)

            for matrix_type in matrix_types:
                builded_automaton = intersect_of_automata(
                    left_automaton, right_automaton, matrix_type
                )

                assert expected_automaton.is_equivalent_to(builded_automaton)


def test_transitive_closure():

    for (
        transitions_list,
        starting_states,
        final_states,
        expected,
    ) in transitive_closure_test:
        nfa = build_nfa(transitions_list, starting_states, final_states)

        for matrix_type in matrix_types:
            binary_matrix = build_binary_matrix_by_nfa(nfa, matrix_type)
            geted_closure = transitive_closure(binary_matrix, matrix_type)

            match matrix_type:
                case "lil":
                    expected_closure = lil_matrix(expected)
                case "dok":
                    expected_closure = dok_matrix(expected)
                case "csr":
                    expected_closure = csr_matrix(expected)
                case "csc":
                    expected_closure = csc_matrix(expected)

            assert geted_closure.toarray().data == expected_closure.toarray().data
