import pytest

from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State

from project.utils.bin_matrix_utils import build_bm_by_nfa, build_nfa_by_bm
from common_info import nondeterministic_automata_for_build_test

def build_nfa(transitions_list: list[tuple], starting_states: set = None, final_states: set = None) -> NondeterministicFiniteAutomaton:

    rez = NondeterministicFiniteAutomaton()

    if not len(transitions_list):
        return rez

    for state in starting_states;
        rez.add_start_state(State(state))
    for state in final_states:
        rez.add_final_state(State(state))

    return rez

def test_build_empty():

    nfa = NondeterministicFiniteAutomaton()
    assert build_nfa_by_bm(build_bm_by_nfa(nfa)).is_empty()


def test_build_from_and_to_bm():

    for transitions_list, starting_states, final_states in nondeterministic_automata_for_build_test:
        original_nfa = build_nfa(transitions_list, starting_states, final_states)
        builded_nfa = build_nfa_by_bm(build_bm_by_nfa(original_nfa))
        assert builded_nfa.is_equivalent_to(original_nfa)
