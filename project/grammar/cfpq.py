from typing import Callable

from pyformlang.cfg import Variable, Terminal, Epsilon, CFG
from networkx import Graph
from scipy.sparse import dok_array, csr_array, eye

from project.utils.grammar_utils import contex_free_to_weak_chomsky_form


def helling_request(
    graph: Graph,
    request: CFG,
    starting_vertices: set = None,
    final_vertices: set = None,
    starting_symbol: str | Variable = "S",
) -> set:

    """
    From given starting and finale vertices finds pairs that are connected by path
    satisfying contex free grammar in given graph

    Args:
        graph: graph to find paths
        request: contex grammar that represent request
        starting_vertices: set of starting vertices
        final_vertices: set of finale vertices
        starting_symbol: starting nonterminal to grammar

    Returns:
        Set of pair of vertices that connected by satisfying path
    """

    return cfpq_request_with_custom_transitive_closure(
        graph,
        request,
        starting_vertices,
        final_vertices,
        starting_symbol,
        helling_constrained_transitive_closure,
    )


def matrix_request(
    graph: Graph,
    request: CFG,
    starting_vertices: set = None,
    final_vertices: set = None,
    starting_symbol: str | Variable = "S",
) -> set:

    return cfpq_request_with_custom_transitive_closure(
        graph,
        request,
        starting_vertices,
        final_vertices,
        starting_symbol,
        matrix_constrained_transitive_closure,
    )


def cfpq_request_with_custom_transitive_closure(
    graph: Graph,
    request: CFG,
    transitive_closure_function: Callable,
    starting_vertices: set = None,
    final_vertices: set = None,
    starting_symbol: str | Variable = "S",
) -> set:

    if not isinstance(starting_symbol, Variable):
        starting_symbol = Variable(starting_symbol)
    if starting_vertices is None:
        starting_vertices = graph.nodes
    if final_vertices is None:
        final_vertices = graph.nodes
    if starting_symbol is None:
        starting_symbol = request.start_symbol

    transitive_closure = transitive_closure_function(graph, request)

    return {
        (start_node, end_node)
        for start_node, variable, end_node in transitive_closure
        if start_node in starting_vertices
        and variable == starting_symbol
        and end_node in final_vertices
    }


def helling_constrained_transitive_closure(
    graph: Graph, contex_free_grammar: CFG
) -> set:

    """
    Calculates transitive closure of graph with constrained by given grammar

    Args:
        graph: graph with necessary information
        contex_free_grammar: contex free grammar that represent constrains

    Returns:
        Transitive closure of graph
    """

    weak_form_of_grammar = contex_free_to_weak_chomsky_form(contex_free_grammar)

    epsilon_productions: set[Variable] = set()
    terminal_productions: dict[Variable, set[Terminal]] = {}
    variable_productions: dict[Variable, set[tuple[Variable, Variable]]] = {}

    for production in weak_form_of_grammar.productions:
        match production.body:
            case [Epsilon()]:
                epsilon_productions.add(production.head)
            case [Terminal() as terminal]:
                terminal_productions.setdefault(production.head, set()).add(terminal)
            case [Variable() as first_variable, Variable() as second_variable]:
                variable_productions.setdefault(production.head, set()).add(
                    (first_variable, second_variable)
                )

    result = {
        (node, variable, node)
        for node in graph.nodes
        for variable in epsilon_productions
    } | {
        (first_node, variable, second_node)
        for first_node, second_node, label in graph.edges.data("label")
        for variable in terminal_productions
        if Terminal(label) in terminal_productions[variable]
    }

    queue = result.copy()

    while len(queue) > 0:
        first_start, first_variable, first_end = queue.pop()

        tmp = set()
        for second_start, second_variable, second_end in result:
            if first_start == second_end:
                for variable in variable_productions:
                    if (second_variable, first_variable) in variable_productions[
                        variable
                    ] and (second_start, variable, first_start) not in result:
                        queue.add((second_start, variable, first_end))
                        tmp.add((second_start, variable, first_end))
            if second_start == first_end:
                for variable in variable_productions:
                    if (first_variable, second_variable) in variable_productions[
                        variable
                    ] and (first_start, variable, second_end) not in result:
                        queue.add((first_start, variable, second_end))
                        tmp.add((first_start, variable, second_end))

        result |= tmp

    return result


def matrix_constrained_transitive_closure(
    graph: Graph, contex_free_grammar: CFG
) -> set:

    weak_form_of_grammar = contex_free_to_weak_chomsky_form(contex_free_grammar)

    epsilon_productions: set[Variable] = set()
    terminal_productions: dict[Variable, set[Terminal]] = {}
    variable_productions: dict[Variable, set[tuple[Variable, Variable]]] = {}

    for production in weak_form_of_grammar.productions:
        match production.body:
            case [Epsilon()]:
                epsilon_productions.add(production.head)
            case [Terminal() as terminal]:
                terminal_productions.setdefault(production.head, set()).add(terminal)
            case [Variable() as first_variable, Variable() as second_variable]:
                variable_productions.setdefault(production.head, set()).add(
                    (first_variable, second_variable)
                )

    nodes_indexes = {node: index for index, node in enumerate(graph.nodes)}
    matrixes: dict[Variable, dok_array] = {
        variable: dok_array((len(nodes_indexes), len(nodes_indexes)), dtype=bool)
        for variable in weak_form_of_grammar.variables
    }

    for first_node, second_node, label in graph.edges.data("label"):
        index_from = nodes_indexes[first_node]
        index_to = nodes_indexes[second_node]
        for variable in terminal_productions.setdefault(1, set()):
            matrixes[variable][index_from, index_to] = True

    for matrix in matrixes.values():
        matrix.tocsr()

    diagonal = csr_array(eye(len(nodes_indexes), dtype=bool))
    for variable in epsilon_productions:
        matrixes[variable] += diagonal

    changed = True
    while changed:
        changed = False
        for head, first_body, second_body in variable_productions:
            old_nnz = matrixes[head].nnz
            matrixes[head] += matrixes[first_body] @ matrixes[second_body]
            changed |= matrixes[head].nnz != old_nnz

    reversed_nodes_indexes = {index: node for node, index in nodes_indexes.items()}
    result = set()
    for variable, matrix in matrixes.items():
        for index_from, index_to in zip(*matrix.nonezero()):
            result.add(
                (
                    reversed_nodes_indexes[index_from],
                    variable,
                    reversed_nodes_indexes[index_to],
                )
            )

    return result
