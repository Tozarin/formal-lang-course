from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    State,
)
from networkx import MultiDiGraph

from project.utils.bin_matrix_utils import (
    build_bm_by_nfa,
    build_nfa_by_bm,
    intersect_of_automata_by_binary_matixes,
)


class AutomataExepction(Exception):
    def __init__(self, msg: str):
        self.message = msg


def gen_min_dfa_by_reg(reg: Regex) -> DeterministicFiniteAutomaton:

    """
    Generate minimal deterministic finite automaton by regular expression

    Args:
        reg: regular expression that automata would recognize

    Returns:
        Genereted automata
    """

    return reg.to_epsilon_nfa().minimize()


def gen_nfa_by_graph(
    graph: MultiDiGraph, starting_vertices: set = None, final_vertices: set = None
) -> NondeterministicFiniteAutomaton:

    """
    Generate nondeterministic finite automaton by graph with given start and finale states

    Args:
        graph: graph that would be base for automata
        start_vs: set of vertexes that would be start states
        fin_vs: set of vertexes that would be finale states

    Returns:
        Genereted automata
    """

    nfa = NondeterministicFiniteAutomaton()

    nfa.add_transitions(
        set(
            map(
                lambda e: (e[0], e[2]["label"], e[1])
                if "label" in e[2].keys()
                else None,
                graph.edges.data(),
            )
        )
    )

    nodes = set(graph)

    if not starting_vertices:
        starting_vertices = nodes
    if not final_vertices:
        final_vertices = nodes

    if not starting_vertices.issubset(nodes):
        raise AutomataExepction("Starting nodes are not subset of graph")
    if not final_vertices.issubset(nodes):
        raise AutomataExepction("Finale nodes are not subset of graph")

    for vertex in starting_vertices:
        nfa.add_start_state(State(vertex))
    for vertex in final_vertices:
        nfa.add_final_state(State(vertex))

    return nfa


def intersect_of_automata(
    left_nfa: NondeterministicFiniteAutomaton,
    right_nfa: NondeterministicFiniteAutomaton,
) -> NondeterministicFiniteAutomaton:

    """
    Calculates intersect of given automata

    Args:
        left_nfa: left side automaton
        right_nfa: right side automaton

    Returns:
        Intersect of automata
    """

    left_bin_matrix, right_bin_matrix = build_bm_by_nfa(left_nfa), build_bm_by_nfa(
        right_nfa
    )

    rez_bin_matrix = intersect_of_automata_by_binary_matixes(
        left_bin_matrix, right_bin_matrix
    )

    return build_nfa_by_bm(rez_bin_matrix)
