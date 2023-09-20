import pytest

from networkx import algorithms, is_isomorphic, MultiDiGraph, Graph
from pyformlang.finite_automaton import FiniteAutomaton
from pyformlang.regular_expression import Regex

from project.utils.graph_utils import (
    gen_labeled_two_cycles_graph,
    load_from_dot,
    get_graph,
)
from project.utils.automata_utils import (
    gen_min_dfa_by_reg,
    gen_nfa_by_graph,
    AutomataExepction,
)
from common_info import (
    path_to_results,
    path_to_automata,
    path_to_graphs,
    reg_test,
    gen_auto_from_graph_test,
)


def is_isomorphic_fa_and_graph(fa: FiniteAutomaton, gr: MultiDiGraph) -> bool:

    fa_graph = fa.to_networkx()

    for node in list(fa_graph):
        if isinstance(node, str) and node.endswith("_starting"):
            fa_graph.remove_node(node)

    for _, data in fa_graph.nodes.data():
        for i in ("is_start", "is_final"):
            if data[i] in ("True", "False"):
                data[i] = data[i] == "True"

    helper = algorithms.isomorphism.categorical_edge_match("label", None)

    return is_isomorphic(gr, fa_graph, edge_match=helper)


def test_gen_min_dfa_by_reg():
    for reg, path in reg_test:
        fa = gen_min_dfa_by_reg(Regex(reg))
        graph = load_from_dot(path_to_automata + path)
        assert is_isomorphic_fa_and_graph(fa, graph)


def test_fail_gen_nfa_by_graph():

    count_of_nodes = 10
    graph = gen_labeled_two_cycles_graph(
        count_of_nodes // 2, count_of_nodes // 2, ("a", "b")
    )

    set_of_vertexes = set(graph)
    set_of_vertexes.add(count_of_nodes + 1)

    try:
        fa = gen_nfa_by_graph(graph, set_of_vertexes, None)
        assert False
    except AutomataExepction:
        assert True

    try:
        fa = gen_nfa_by_graph(graph, None, set_of_vertexes)
        assert False
    except AutomataExepction:
        assert True


def test_gen_nfa_by_graph():
    for path in gen_auto_from_graph_test:
        graph = load_from_dot(path_to_graphs + path)
        fa = gen_nfa_by_graph(graph)
        assert is_isomorphic_fa_and_graph(fa, graph)


def test_gen_nfa_by_remoted_graph():
    graph = get_graph("skos")
    fa = gen_nfa_by_graph(graph)
    assert is_isomorphic_fa_and_graph(fa, graph)


def test_gen_nfa_by_two_cycles_graph():
    graph = gen_labeled_two_cycles_graph(2, 2, ("a", "b"))
    fa = gen_nfa_by_graph(graph, {0}, {1})
    assert is_isomorphic_fa_and_graph(fa, graph)
