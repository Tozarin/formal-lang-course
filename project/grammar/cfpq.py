from typing import Callable

from pyformlang.cfg import Variable, Terminal, Epsilon, CFG
from networkx import Graph
from scipy.sparse import dok_array, csr_array, eye

from project.utils.grammar_utils import contex_free_to_weak_chomsky_form
from project.grammar.recursive_state_machines import (
    build_binary_matrix_by_rsm,
    minimize_recursive_state_machine,
    recursive_state_machine_from_extended_contex_free_grammar,
)
from project.utils.bin_matrix_utils import (
    build_binary_matrix_by_nfa,
    transitive_closure,
    intersect_of_automata_by_binary_matixes,
)
from project.utils.automata_utils import gen_nfa_by_graph
from project.grammar.extended_contex_free_grammar import extend_contex_free_grammar


def helling_request(
    graph: Graph,
    request: CFG,
    starting_vertices: set = None,
    final_vertices: set = None,
    starting_symbol: str | Variable = "S",
) -> set:

    """
    From given starting and finale vertices finds pairs that are connected by path
    satisfying contex free grammar in given graph by Helling's algorithm

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
        helling_constrained_transitive_closure,
        starting_vertices,
        final_vertices,
        starting_symbol,
    )


def matrix_request(
    graph: Graph,
    request: CFG,
    starting_vertices: set = None,
    final_vertices: set = None,
    starting_symbol: str | Variable = "S",
) -> set:

    """
    From given starting and finale vertices finds pairs that are connected by path
    satisfying contex free grammar in given graph by matrix algorithm

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
        matrix_constrained_transitive_closure,
        starting_vertices,
        final_vertices,
        starting_symbol,
    )


def tensor_request(
    graph: Graph,
    request: CFG,
    starting_vertices: set = None,
    final_vertices: set = None,
    starting_symbol: str | Variable = "S",
) -> set:

    """
    From given starting and finale vertices finds pairs that are connected by path
    satisfying contex free grammar in given graph by tensor algorithm

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
        tensor_constrained_transitive_closure,
        starting_vertices,
        final_vertices,
        starting_symbol,
    )


def cfpq_request_with_custom_transitive_closure(
    graph: Graph,
    request: CFG,
    transitive_closure_function: Callable,
    starting_vertices: set = None,
    final_vertices: set = None,
    starting_symbol: str | Variable = "S",
) -> set:

    """
    Support function that represents given arguments in from to be
    returned as request answer

    Args:
        graph: graph to find paths
        request: contex grammar that represent request
        transitive_closure_function: function to transitive closure
        starting_vertices: set of starting vertices
        final_vertices: set of finale vertices
        starting_symbol: starting nonterminal to grammar

    Returns:
        Set of pair of vertices that connected by satisfying path
    """

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
    by Helling's algorithm

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

    """
    Calculates transitive closure of graph with constrained by given grammar
    by matrix algorithm

    Args:
        graph: graph with necessary information
        contex_free_grammar: contex free grammar that represent constrains

    Returns:
        Transitive closure of graph
    """

    weak_form_of_grammar = contex_free_to_weak_chomsky_form(contex_free_grammar)

    epsilon_productions = set()
    terminal_productions = {}
    variable_productions = set()

    for production in weak_form_of_grammar.productions:
        match production.body:
            case [Epsilon()]:
                epsilon_productions.add(production.head)
            case [Terminal() as terminal]:
                terminal_productions.setdefault(terminal.value, set()).add(
                    production.head
                )
            case [Variable() as first_variable, Variable() as second_variable]:
                variable_productions.add(
                    (production.head, first_variable, second_variable)
                )

    nodes_indexes = {node: index for index, node in enumerate(graph.nodes)}
    matrixes: dict[Variable, dok_array] = {
        variable: dok_array((len(nodes_indexes), len(nodes_indexes)), dtype=bool)
        for variable in weak_form_of_grammar.variables
    }

    for node_from, node_to, label in graph.edges.data("label"):
        index_from = nodes_indexes[node_from]
        index_to = nodes_indexes[node_to]
        for variable in terminal_productions.setdefault(label, set()):
            matrixes[variable][index_from, index_to] = True

    for matrix in matrixes.values():
        matrix.tocsr()

    diagonal = csr_array(eye(len(nodes_indexes), dtype=bool))
    for variable in epsilon_productions:
        matrixes[variable] += diagonal

    changed_flag = True
    while changed_flag:
        changed_flag = False
        for head, first_body, second_body in variable_productions:
            nnz_old = matrixes[head].nnz
            matrixes[head] += matrixes[first_body] @ matrixes[second_body]
            changed_flag |= matrixes[head].nnz != nnz_old

    reversed_nodes_indexes = {index: node for node, index in nodes_indexes.items()}
    result = set()
    for variable, matrix in matrixes.items():
        for index_from, index_to in zip(*matrix.nonzero()):
            result.add(
                (
                    reversed_nodes_indexes[index_from],
                    variable,
                    reversed_nodes_indexes[index_to],
                )
            )

    return result


def tensor_constrained_transitive_closure(
    graph: Graph, contex_free_grammar: CFG
) -> set:

    """
    Calculates transitive closure of graph with constrained by given grammar
    by tensor algorithm

    Args:
        graph: graph with necessary information
        contex_free_grammar: contex free grammar that represent constrains

    Returns:
        Transitive closure of graph
    """

    binary_matrix_of_rsm = build_binary_matrix_by_rsm(
        minimize_recursive_state_machine(
            recursive_state_machine_from_extended_contex_free_grammar(
                extend_contex_free_grammar(contex_free_grammar),
                contex_free_grammar.start_symbol,
            )
        )
    )
    binary_matrix_of_graph = build_binary_matrix_by_nfa(gen_nfa_by_graph(graph))
    count_of_graph_states = len(binary_matrix_of_graph.states)

    diagonal = csr_array(eye(len(binary_matrix_of_graph.states), dtype=bool))
    for variable in contex_free_grammar.get_nullable_symbols():
        binary_matrix_of_graph.matrix[variable.value] += diagonal

    transitive_closure_size = 0
    while True:
        transitive_closure_intersects = list(
            zip(
                *transitive_closure(
                    intersect_of_automata_by_binary_matixes(
                        binary_matrix_of_rsm, binary_matrix_of_graph
                    )
                )
            )
        )

        if len(transitive_closure_intersects) == transitive_closure_size:
            break
        transitive_closure_size = len(transitive_closure_intersects)

        for i, j in transitive_closure_intersects:
            rsm_i, rsm_j = i // count_of_graph_states, j // count_of_graph_states
            start_state, final_state = (
                binary_matrix_of_rsm.states[rsm_i],
                binary_matrix_of_rsm.states[rsm_j],
            )
            if start_state.is_start and final_state.is_final:
                value = start_state.value[0]

                graph_i, graph_j = i % count_of_graph_states, j % count_of_graph_states
                graph_matrix = csr_array(
                    ([True], ([graph_i], [graph_j])),
                    shape=((count_of_graph_states, count_of_graph_states)),
                    dtype=bool,
                )

                if value in binary_matrix_of_graph.matrix:
                    binary_matrix_of_graph.matrix[value] += graph_matrix
                else:
                    binary_matrix_of_graph.matrix[value] = graph_matrix.copy()

    result = set()
    for variable, matrix in binary_matrix_of_graph.matrix.items():
        if isinstance(variable, Variable):
            for i, j in zip(*matrix.nonzero()):
                result.add(
                    (
                        binary_matrix_of_graph.states[i].value,
                        variable,
                        binary_matrix_of_graph.states[j].value,
                    )
                )

    return result
