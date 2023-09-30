import pytest

from filecmp import cmp

from cfpq_data import labeled_two_cycles_graph
from networkx import MultiDiGraph, algorithms, is_isomorphic
from pyformlang.regular_expression import Regex

from project.utils.graph_utils import (
    gen_labeled_two_cycles_graph,
    get_graph,
    get_info,
    get_set_of_edges,
    regular_request,
    bfs_regular_request,
    save_as_dot,
    load_from_dot,
)
from common_info import (
    path_to_graphs,
    path_to_results,
    path_to_bfs_test_graphs,
    regular_request_test,
    bfs_regular_request_test,
)

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
    for _, _, _, regex, _, _, _ in regular_request_test:
        assert regular_request(graph, {}, {}, Regex(regex)) == set()


def test_regular_request_at_two_cycles_graph():

    for (
        fst_num_nodes,
        snd_num_nodes,
        marks,
        regex,
        starting_states,
        final_states,
        expected_set,
    ) in regular_request_test:
        graph = gen_labeled_two_cycles_graph(fst_num_nodes, snd_num_nodes, marks)
        assert (
            regular_request(graph, starting_states, final_states, Regex(regex))
            == expected_set
        )


def test_bfs_regular_request_at_empty_graph():

    graph = MultiDiGraph()
    for _, regex, _, _, _, _ in bfs_regular_request_test:
        for separeted_flag in [True, False]:
            assert (
                bfs_regular_request(graph, Regex(regex), {}, {}, separeted_flag)
                == set()
            )


def test_bfs_regular_separated_request_at_graph():

    for (
        graph_name,
        regex,
        starting_states,
        final_states,
        separated_variant_expected_set,
        _,
    ) in bfs_regular_request_test:
        graph = load_from_dot(path_to_bfs_test_graphs + graph_name)
        assert (
            bfs_regular_request(
                graph, Regex(regex), starting_states, final_states, True
            )
            == separated_variant_expected_set
        )


def test_bfs_regular_non_separated_request_at_graph():
    for (
        graph_name,
        regex,
        starting_states,
        final_states,
        _,
        non_separated_variant_expected_set,
    ) in bfs_regular_request_test:
        graph = load_from_dot(path_to_bfs_test_graphs + graph_name)
        assert (
            bfs_regular_request(graph, Regex(regex), starting_states, final_states)
            == non_separated_variant_expected_set
        )
