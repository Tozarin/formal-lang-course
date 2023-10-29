from collections import namedtuple
from typing import Set, Tuple

from cfpq_data import download, graph_from_csv, labeled_two_cycles_graph
from networkx import MultiDiGraph, drawing
from pyformlang.regular_expression import Regex
from scipy.sparse import lil_array, csr_array

from project.utils.automata_utils import (
    gen_min_dfa_by_reg,
    gen_nfa_by_graph,
    intersect_of_automata_by_binary_matixes,
)
from project.utils.bin_matrix_utils import (
    BinaryMatrix,
    build_binary_matrix_by_nfa,
    build_nfa_by_binary_matrix,
    transitive_closure,
    direct_sum,
    init_front,
    init_separeted_front,
    sort_left_part_of_front,
    intersect_of_automata_by_binary_matixes,
)

Info = namedtuple("Info", ["num_of_nodes", "num_of_edges", "marks"])


def get_graph(name: str) -> MultiDiGraph:

    """
    Downloads the graph from CFPQ dataset by name

    Args:
        name: name of graph in CFPQ dataset

    Returns:
        Graph downloaded
    """

    graph_path = download(name)
    graph = graph_from_csv(graph_path)

    return graph


def get_info(name: str) -> Info:

    """
    Downloads graph by name from CFPQ dataset, and then
    gets number of nodes, edges and set of different labels of the graph given

    Args:
        name: name of graph in CFPQ dataset to be analyzed

    Returns:
        Info with number of nodes, edges and set of different labels
    """

    graph = get_graph(name)
    marks = set([i[2]["label"] for i in graph.edges.data()])

    return Info(graph.number_of_nodes(), graph.number_of_edges(), marks)


def get_set_of_edges(graph: MultiDiGraph) -> Set[Tuple[any, any, any]]:
    return set(
        map(
            lambda e: (e[0], e[2]["label"], e[1]) if "label" in e[2].keys() else None,
            graph.edges.data(),
        )
    )


def load_from_dot(path: str) -> MultiDiGraph:
    rez = drawing.nx_pydot.read_dot(path)

    if "\\n" in rez:
        rez.remove_node("\\n")

    return rez


def gen_labeled_two_cycles_graph(
    fst_num_nodes: int, snd_num_nodes: int, marks: Tuple[str, str]
) -> MultiDiGraph:

    """
    Creates two cycled graph connected by one node from amount of nodes in cycles and labels

    Args:
        fst_num_nodes: amount of nodes in the first cycle without a common node
        snd_num_nodes: amount of nodes in the second cycle without a common node
        marks: Labels that will be used to mark the edges of the graph

    Returns:
        A graph with two cycles connected by one node with labeled edges
    """

    return labeled_two_cycles_graph(fst_num_nodes, snd_num_nodes, labels=marks)


def save_as_dot(graph: MultiDiGraph, path: str):

    """
    Save graph in the DOT format into the path provided

    Args:
        path: path to be saved to
    """

    drawing.nx_pydot.to_pydot(graph).write_raw(path)


def regular_request(
    graph: MultiDiGraph, starting_vertices: set, final_vertices: set, reg: Regex
) -> set:

    """
    From given starting and finale vertices finds pairs that are connected by path satisfying regular expression in given graph

    Args:
        graph: graph to find paths
        starting_vertices: set of starting vertices
        final_vertices: set of finale vertices
        reg: regular expresiion that paths must satisfy

    Returns:
        Set of pair of vertices that connected by satisfying path
    """

    binary_matrix_of_regular_request = build_binary_matrix_by_nfa(
        gen_min_dfa_by_reg(reg)
    )
    binary_matrix_of_graph = build_binary_matrix_by_nfa(
        gen_nfa_by_graph(graph, starting_vertices, final_vertices)
    )

    intersect = intersect_of_automata_by_binary_matixes(
        binary_matrix_of_graph, binary_matrix_of_regular_request
    )

    tran_closure = transitive_closure(intersect)

    result = set()
    for node_from_index, node_to_index in zip(*tran_closure):
        node_from = intersect.states[node_from_index]
        node_to = intersect.states[node_to_index]
        if node_from.is_start and node_to.is_final:
            start_node = node_from.value[0]
            final_node = node_to.value[0]
            result.add((start_node, final_node))

    return result


def bfs_regular_request(
    graph: MultiDiGraph,
    reg: Regex,
    starting_vertices: set = None,
    final_vertices: set = None,
    separated_flag: bool = False,
) -> set:

    """
    From given final vertices finds ones that are reachable from given statring vertices by path
    satisfying regular expression in given graph xor finds such vertices for each starting vertices separetely

    Args:
        graph: graph to find paths
        reg: regular expresiion that paths must satisfy
        starting_vertices: set of starting vertices
        final_vertices: set of finale vertices
        separeted_flag: flag that represented what kind of result is required

    Returns:
        Set of vertices that are reachable xor set of sets of vertices that are reachable
    """

    binary_matrix_of_graph = build_binary_matrix_by_nfa(
        gen_nfa_by_graph(graph, starting_vertices, final_vertices)
    )
    binary_matrix_of_request = build_binary_matrix_by_nfa(gen_min_dfa_by_reg(reg))

    size_of_graph = len(binary_matrix_of_graph.states)
    size_of_request = len(binary_matrix_of_request.states)

    if not size_of_graph:
        return set()

    direct_sum_of_matrixes = direct_sum(
        binary_matrix_of_request, binary_matrix_of_graph
    )

    starting_indexes = [
        index
        for index, state in enumerate(binary_matrix_of_graph.states)
        if state.is_start
    ]

    front = (
        init_front(
            binary_matrix_of_graph.states,
            binary_matrix_of_request.states,
            lil_array(
                [state.is_start for state in binary_matrix_of_graph.states], dtype=bool
            ),
        )
        if not separated_flag
        else init_separeted_front(
            binary_matrix_of_graph.states,
            binary_matrix_of_request.states,
            starting_indexes,
        )
    )

    visited_states = csr_array(front.shape, dtype=bool)
    direct_sum_of_matrixes = direct_sum(
        binary_matrix_of_request, binary_matrix_of_graph
    )

    while True:
        previos_nnz = visited_states.nnz

        for matrix in direct_sum_of_matrixes.matrix.values():
            new_front = visited_states @ matrix if front is None else front @ matrix
            visited_states += sort_left_part_of_front(size_of_request, new_front)

        front = None

        if visited_states.nnz == previos_nnz:
            break

    result = set()
    for i, j in zip(*visited_states.nonzero()):
        if (
            j >= size_of_request
            and binary_matrix_of_request.states[i % size_of_request].is_final
        ):
            graph_index = j - size_of_request
            if binary_matrix_of_graph.states[graph_index].is_final:
                result.add(
                    graph_index
                    if not separated_flag
                    else (
                        starting_indexes[i // size_of_request],
                        graph_index,
                    )
                )

    return (
        {
            (
                binary_matrix_of_graph.states[i].value,
                binary_matrix_of_graph.states[j].value,
            )
            for i, j in result
        }
        if separated_flag
        else {binary_matrix_of_graph.states[i].value for i in result}
    )
