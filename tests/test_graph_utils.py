from filecmp import cmp

import pytest
from cfpq_data import labeled_two_cycles_graph
from common_info import path_to_graphs, path_to_results, regular_request_test
from networkx import MultiDiGraph, algorithms, is_isomorphic
from pyformlang.regular_expression import Regex

from project.utils.graph_utils import (gen_labeled_two_cycles_graph, get_graph,
                                       get_info, get_set_of_edges,
                                       regular_request, save_as_dot)

sample_info = get_info("skos")


def test_num_of_nodes():
    assert sample_info.num_of_nodes == 144


def test_num_of_edges():
    assert sample_info.num_of_edges == 252


def test_marks():
    assert sample_info.marks == {
        "seeAlso",
        "comment",
        "subPropertyOf",
        "rest",
        "type",
        "creator",
        "inverseOf",
        "label",
        "description",
        "unionOf",
        "domain",
        "range",
        "example",
        "scopeNote",
        "contributor",
        "title",
        "subClassOf",
        "definition",
        "first",
        "disjointWith",
        "isDefinedBy",
    }


def test_raise_not_found():
    try:
        cracked = get_info("not_existed_graph")
        assert cracked.num_nodes == 42
    except FileNotFoundError:
        assert True


def test_gen_labeled_two_cycles_graph():
    cnt_n = (23, 32)
    marks = ("a", "b")

    expc_gr = labeled_two_cycles_graph(cnt_n[0], cnt_n[1], labels=marks)
    actl_gr = gen_labeled_two_cycles_graph(cnt_n[0], cnt_n[1], marks)

    helper = algorithms.isomorphism.categorical_multiedge_match("label", None)

    assert is_isomorphic(actl_gr, expc_gr, edge_match=helper)


def test_save_as_dot():
    path_to_generated = path_to_results + "generated_graph.dot"
    path_to_sample = path_to_graphs + "sample_graph.dot"

    gr = gen_labeled_two_cycles_graph(2, 2, ("a", "b"))
    save_as_dot(gr, path_to_generated)

    assert cmp(path_to_generated, path_to_sample, shallow=False)


def test_get_edges_unique_by_marks():

    gr = gen_labeled_two_cycles_graph(2, 2, ("a", "b"))
    ls = get_set_of_edges(gr)

    assert ls == {
        (0, "b", 3),
        (2, "a", 0),
        (0, "a", 1),
        (4, "b", 0),
        (1, "a", 2),
        (3, "b", 4),
        (4, "b", 0),
    }


def test_regular_request_at_empty_graph():

    graph = MultiDiGraph()
    for _, _, _, reg, _, _, _ in regular_request_test:
        assert regular_request(graph, [], [], Regex(reg)) == set()


def test_regular_request_at_two_cycles_graph():

    for (
        fst_num_nodes,
        snd_num_nodes,
        marks,
        reg,
        starting_states,
        finale_states,
        expected_set,
    ) in regular_request_test:
        graph = gen_labeled_two_cycles_graph(fst_num_nodes, snd_num_nodes, marks)
        assert (
            regular_request(graph, starting_states, finale_states, Regex(reg)) == set()
        )
