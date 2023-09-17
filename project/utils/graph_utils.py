from cfpq_data import download, graph_from_csv, labeled_two_cycles_graph
from networkx import MultiDiGraph, drawing
from typing import Tuple, Set
from collections import namedtuple

Info = namedtuple("Info", ["num_of_nodes", "num_of_edges", "marks"])


def get_graph(name: str) -> MultiDiGraph:

    graph_path = download(name)
    graph = graph_from_csv(graph_path)

    return graph


def get_info(name: str) -> Info:

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
    rez.remove_node("\\n")
    return rez


def gen_labeled_two_cycles_graph(
    fst_num_nodes: int, snd_num_nodes: int, marks: Tuple[str, str]
) -> MultiDiGraph:
    return labeled_two_cycles_graph(fst_num_nodes, snd_num_nodes, labels=marks)


def save_as_dot(graph: MultiDiGraph, path: str):
    drawing.nx_pydot.to_pydot(graph).write_raw(path)
