from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import DeterministicFiniteAutomaton, NondeterministicFiniteAutomaton
from networkx import MultiDiGraph

def gen_min_dfa_by_reg(reg: Regex) -> DeterministicFiniteAutomaton:
    return reg.to_epsilon_nfa().minimize()

def gen_nfa_by_graph(graph: MultiDiGraph, start_vs: set = None, fin_vs: set = None) -> NondeterministicFiniteAutomaton:
    
    nfa = NondeterministicFiniteAutomaton()

    return nfa