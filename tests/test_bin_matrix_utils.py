import pytest

from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State

from project.utils.bin_matrix_utils import build_bm_by_nfa, build_nfa_by_bm


def test_build_empty():

    nfa = NondeterministicFiniteAutomaton()
    assert build_nfa_by_bm(build_bm_by_nfa(nfa)).is_empty()


def test_build_bm_by_nfa():
    assert True


def test_build_nfa_by_bm():
    assert True
