import pytest

from cfpq_data import labeled_two_cycles_graph
from filecmp import cmp
from networkx import algorithms, is_isomorphic

from project.utils.graph_utils import (
    get_info,
    gen_labeled_two_cycles_graph,
    save_as_dot,
)

path_to_results = "tests/results/"

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
    path_to_sample = path_to_results + "sample_graph.dot"

    gr = gen_labeled_two_cycles_graph(2, 2, ("a", "b"))
    save_as_dot(gr, path_to_generated)

    assert cmp(path_to_generated, path_to_sample, shallow=False)
