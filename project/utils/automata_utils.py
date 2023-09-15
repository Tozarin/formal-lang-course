from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    State,
)
from networkx import MultiDiGraph
from utils.graph_utils import get_set_of_edges


class AutomataExepction(Exception):
    def __init__(self, msg: str):
        self.message = msg


def gen_min_dfa_by_reg(reg: Regex) -> DeterministicFiniteAutomaton:
    return reg.to_epsilon_nfa().minimize()


def gen_nfa_by_graph(
    graph: MultiDiGraph, start_vs: set = None, fin_vs: set = None
) -> NondeterministicFiniteAutomaton:

    nfa = NondeterministicFiniteAutomaton()
    nfa.add_transitions(get_set_of_edges(graph))

    nodes = set(graph)

    if not start_vs:
        start_vs = nodes
    if not fin_vs:
        fin_vs = nodes

    if not start_vs.issubset(nodes):
        raise AutomataExepction("Starting nodes are not subset of graph")
    if not fin_vs.issubset(nodes):
        raise AutomataExepction("Finale nodes are not subset of graph")

    for s in start_vs:
        nfa.add_start_state(State(s))
    for s in fin_vs:
        nfa.add_final_state(State(s))

    return nfa
