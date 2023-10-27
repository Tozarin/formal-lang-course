import pytest

from pyformlang.cfg import Variable

from project.grammar.cfpq import (
    helling_constrained_transitive_closure,
    helling_request,
)
from project.utils.graph_utils import load_from_dot
from project.utils.grammar_utils import read_contex_free_grammar_from_file
from common_info import (
    path_to_graphs,
    path_to_grammars,
    constrained_transitive_closure_examples,
    helling_examples,
)


def test_helling_constrained_transitive_closure():

    for (
        test_graph_name,
        test_grammar_name,
        expected_answer,
    ) in constrained_transitive_closure_examples:
        test_graph = load_from_dot(path_to_graphs + test_graph_name)
        test_grammar = read_contex_free_grammar_from_file(
            path_to_grammars + test_grammar_name
        )

        expected_answer = {
            (start_node, Variable(variable), end_node)
            for start_node, variable, end_node in expected_answer
        }

        assert (
            helling_constrained_transitive_closure(test_graph, test_grammar)
            == expected_answer
        )


def test_helling_request():

    for (
        test_graph_name,
        starting_vertices,
        final_vertices,
        starting_symbol,
        test_grammar_name,
        expected_answer,
    ) in helling_examples:
        test_graph = load_from_dot(path_to_graphs + test_graph_name)
        test_grammar = read_contex_free_grammar_from_file(
            path_to_grammars + test_grammar_name
        )

        assert (
            helling_request(
                test_graph,
                test_grammar,
                starting_vertices,
                final_vertices,
                starting_symbol,
            )
            == expected_answer
        )
