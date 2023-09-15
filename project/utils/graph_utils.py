import cfpq_data

from networkx import MultiDiGraph, drawing
from typing import Tuple
from collections import namedtuple

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


def gen_labeled_two_cycles_graph(
    fst_num_nodes: int, snd_num_nodes: int, marks: Tuple[str, str]
) -> MultiDiGraph:

    """
    Creates two cycled graph connected by one node from amount of nodes in cycles and labels

    Args:
        n: amount of nodes in the first cycle without a common node
        m: amount of nodes in the second cycle without a common node
        labels: Labels that will be used to mark the edges of the graph

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
