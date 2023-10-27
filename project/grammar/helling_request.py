from pyformlang.cfg import CFG, Variable, Terminal, Epsilon
from networkx import Graph

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

    if not isinstance(starting_symbol, Variable):
        starting_symbol = Variable(starting_symbol)
    if starting_vertices is None:
        starting_vertices = graph.nodes
    if final_vertices is None:
        final_vertices = graph.nodes
    if starting_symbol is None:
        starting_symbol = request.start_symbol

    constrained_transitive_closure = constrained_transitive_closure(graph, request)

    return {
        (start_node, end_node)
        for start_node, variable, end_node in constrained_transitive_closure
        if start_node in starting_vertices
        and variable == starting_symbol
        and end_node in final_vertices
    }


def constrained_transitive_closure(graph: Graph, contex_free_grammar: CFG) -> set:

    """
    Calculates transitive closure of graph with constrained by given grammar

    Args:
        graph: graph with necessary information
        contex_free_grammar: contex free grammar that represent constrains

    Returns:
        Transitive closure of graph
    """

    weak_form_of_grammar = contex_free_to_weak_chomsky_form(
        contex_free_grammar
    )

    epsilon_productions: set[Variable] = set()
    terminal_productions: dict[Variable, set[Terminal]] = {}
    variable_productions: dict[Variable, set[tuple[Variable, Variable]]] = {}

    for production in weak_form_of_grammar.productions:
        match production.body:
            case [Epsilone()]:
                epsilon_productions.add(production.head)
            case [Terminal as terminal]:
                terminal_productions.setdefault(production.head, set()).add(terminal)
            case [Variable() as first_variable, Variable() as second_variable]:
                variable_productions.setdefault(production.head, set()).add(
                    first_variable, second_variable
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
