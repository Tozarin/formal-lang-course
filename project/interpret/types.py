from abc import ABC, abstractmethod
from pathlib import Path
from copy import copy

from pyformlang.cfg import CFG
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.regular_expression import Regex
from networkx.drawing.nx_pydot import read_dot

from project.grammar.extended_contex_free_grammar import extend_contex_free_grammar
from project.grammar.recursive_state_machines import recursive_state_machine_from_extended_contex_free_grammar, reachables
from project.utils.grammar_utils import read_contex_free_grammar_from_file
from project.utils.automata_utils import gen_nfa_by_graph, gen_min_dfa_by_reg, intersect_of_automata
from project.utils.graph_utils import get_graph
from project.utils.bin_matrix_utils import build_binary_matrix_by_nfa, transitive_closure

class LSet():
    def __init__(self, elems: set, ttype=None):
        if len(elems) == 0:
            self.type = None
        else:
            if ttype is None:
                iterator = iter(elems)
                self.type = type(next(iterator))

                if not all(isinstance(elem, self.type) for elem in iterator):
                    raise TypeError("Elements of set must be same type")

            else:
                self.type = None

        self.set = elems

    def __eq__(self, second: "LSet") -> bool:
        if self.type != second.type:
            raise TypeError("To equal sets must be same type")

        return self.set == second.set

    def __str__(self) -> str:
        if self.type is None:
            return "<||>"

        return "<|" + ", ".join(str(elem) for elem in self.set) + "|>"

    def __contains__(self, elem) -> bool:
        if not isinstance(elem, self.type):
            raise TypeError("To contains element type must be same as set type")
        return not (self.type is None) and elem in self.set

    def __len__(self) -> int:
        return len(self.set) 

    def __hash__(self):
        return hash(self.set)

    __repr__ = __str__

class LPair():
    def __init__(self, starting, final):
        if type(starting) != type(final):
            raise TypeError("Types of starting and final nodes of edge must be same type")

        self.starting = starting
        self.final = final
        self.type = type(starting)

    def to_tuple(self):
        return (self.starting, self.final)

    def __str__(self) -> str:
        return f"{self.starting} -> {self.final}"

    def __eq__(self, second: "LPair") -> bool:
        if self.type != second.type:
            raise TypeError("To equal pairs must be same type")
            
        return self.starting == second.starting and self.final == second.final

    def __hash__(self):
        return hash(self.to_tuple())

    __repr__ = __str__

class LTriple():
    def __init__(self, starting, mark, final):
        if type(starting) != type(final):
            raise TypeError("Types of starting and final nodes of edge must be same type")

        self.starting = starting
        self.final = final
        self.mark = mark
        self.type = type(starting)

    def to_tuple(self):
        return (self.starting, self.mark, self.final)

    def __str__(self) -> str:
        return f"{self.starting} -- {self.mark} -> {self.final}"

    def __eq__(self, second: "LTriple") -> bool:
        if self.type != second.type:
            raise TypeError("To equal triples must be same type")

        return self.starting == second.starting and self.final == second.final and self.mark == second.mark

    def __hash__(self):
        return hash(self.to_tuple())

    __repr__ = __str__

class LAutoma():
    @abstractmethod
    def from_file(self, path: Path) -> "LAutoma":
        ...

    @abstractmethod
    def from_string(self, string: str) -> "LAutoma":
        ...

    @abstractmethod
    def set_starting(self, starting: LSet) -> "LAutoma":
        ...

    @abstractmethod
    def set_final(self, final: LSet) -> "LAutoma":
        ...

    @abstractmethod
    def add_starting(self, starting: LSet) -> "LAutoma":
        ...

    @abstractmethod
    def add_final(self, final: LSet) -> "LAutoma":
        ...

    @abstractmethod
    def starting(self) -> LSet:
        ...

    @abstractmethod
    def final(self) -> LSet:
        ...

    @abstractmethod
    def reachables(self) -> LSet:
        ...

    @abstractmethod
    def marks(self) -> LSet:
        ...

    @abstractmethod
    def edges(self) -> LSet:
        ...

    @abstractmethod
    def nodes(self) -> LSet:
        ...

    @abstractmethod
    def intersect(self, second: "LAutoma") -> "LAutoma":
        ...

    @abstractmethod
    def union(self, second: "LAutoma") -> "LAutoma":
        ...

    @abstractmethod
    def concat(self, second: "LAutoma") -> "LAutoma":
        ...

class LCFG(LAutoma, ABC):
    def __init__(self, grammar: CFG):
        self.grammar = grammar
        self.type = LSet({variable.value for variable in grammar.variables}).type
        extednded_grammar = extend_contex_free_grammar(grammar)
        self.rsm = recursive_state_machine_from_extended_contex_free_grammar(extednded_grammar, extednded_grammar.starting_symbol)

    def __str__(self) -> str:
        return self.grammar.to_text()

    def __eq__(self, second: "LCFG") -> bool:
        return self.grammar == second.grammar and self.type == second.type and self.rsm == second.rsm

    @classmethod
    def from_file(cfg_class, path: Path) -> "LCFG":
        return cfg_class(read_contex_free_grammar_from_file(path))

    @classmethod
    def from_string(cfg_class, string: str) -> "LCFG":
        return cfg_class(CFG.from_text(string))

    def set_starting(self, starting: LSet) -> "LCFG":
        raise NotImplementedError("Cant change CFG starting symbols after creation in \"set_starting\"")

    def set_final(self, final: LSet) -> "LCFG":
        raise NotImplementedError("Cant change CFG final symbols after creation in \"set_final\"")

    def add_starting(self, starting: LSet) -> "LCFG":
        raise NotImplementedError("Cant change CFG starting symbols after creation in \"add_starting\"")

    def add_final(self, final: LSet) -> "LCFG":
        raise NotImplementedError("Cant change CFG final symbols after creation in \"add_final\"")

    def starting(self) -> "LSet":
        return LSet({state.value for state in self.rsm.subautomata[self.rsm.starting_symbol].start_states})

    def final(self) -> "LSet":
        return LSet({state.value for state in self.rsm.subautomata[self.rsm.starting_symbol].final_states})

    def reachables(self) -> "LSet":
        return LSet({LPair(state_from.value, state_to.value) for (state_from, state_to) in reachables(self.rsm)})

    def marks(self) -> "LSet":
        return LSet({edge[2]["label"] for subautoma in self.rsm.subautomatons.values() for edge in subautomata.edges.data})

    def edges(self) -> "LSet":
        return LSet({LTriple(edge[0], edge[2]["label"], edge[1]) for subautoma in self.rsm.subautomatons.values() for edge in subautoma.edges.data})

    def nodes(self) -> "LSet":
        return LSet({state.value for subautoma in self.rsm.subautomatons.values() for state in subautoma.states})

    def intersect(self, second: "LAutoma") -> "LCFG":
        if isinstance(second, LFiniteAutoma):
            return LCFG(self.grammar.intersection(second.nfa))

        raise TypeError("Cant intersect CFG with another CFG")

    def union(self, second: "LAutoma") -> "LCFG":
        if isinstance(second, LCFG):
            return LCFG(self.grammar.union(second.grammar))

        raise TypeError("Cant union CFG with FA")

    def concat(self, second: "LAutoma") -> "LCFG":
        if isinstance(second, LCFG):
            return LCFG(self.grammar.concatenate(second.grammar))

        raise TypeError("Cant concat CFG with FA")

    __repr__ = __str__

class LFiniteAutoma(LAutoma, ABC):
    def __init__(self, nfa: NondeterministicFiniteAutomaton, ttype=None):
        self.nfa = nfa
        self.type = LSet({state.value for state in nfa.states}, ttype).type

    def __str__(self) -> str:
        return str(self.nfa)

    def __eq__(self, second: "LFiniteAutoma") -> bool:
        return self.type == second.type and self.nfa == second.nfa

    @classmethod
    def from_file(fa_class, path: Path) -> "LFiniteAutoma":
        with open(path, "r") as file:
            return fa_class(gen_nfa_by_graph(read_dot(file)))

    @classmethod
    def from_string(fa_class, string: str) -> "LFiniteAutoma":
        return fa_class(gen_min_dfa_by_reg(Regex(string)))

    @classmethod
    def from_data(fa_class, name: str) -> "LFiniteAutoma":
        return fa_class(gen_nfa_by_graph(get_graph(name)))

    def set_starting(self, starting: LSet) -> "LFiniteAutoma":
        if isinstance(None, starting.type):
            starting = LSet({state.value for state in self.nfa.states})
        if self.type != starting.type:
            raise TypeError(f"To \"set_starting\" expected set of elemets of type {self.type}, but gotted {starting.type}")

        return LFiniteAutoma(NondeterministicFiniteAutomaton(states=copy(self.nfa.states), input_symbols=copy(self.nfa.symbols), start_state=starting.set, final_states=copy(self.nfa.final_states)))

    def set_final(self, final: LSet) -> "LFiniteAutoma":
        if isinstance(None, final.type):
            final = LSet({state.value for state in self.nfa.states})
        if self.type != final.type:
            raise TypeError(f"To \"set_final\" expected set of elemets of type {self.type}, but gotted {final.type}")

        return LFiniteAutoma(NondeterministicFiniteAutomaton(states=copy(self.nfa.states), input_symbols=copy(self.nfa.symbols), start_state=copy(self.nfa.start_states), final_states=final.set))

    def add_starting(self, starting: LSet) -> "LFiniteAutoma":
        if isinstance(None, starting.type) and self.type != starting.type:
            raise TypeError(f"To \"add_starting\" expected set of elemets of type {self.type}, but gotted {starting.type}")

        return LFiniteAutoma(NondeterministicFiniteAutomaton(states=copy(self.nfa.states), input_symbols=copy(self.nfa.symbols), start_state=copy(self.nfa.start_states).union(starting.set), final_states=copy(self.nfa.final_states)))

    def add_final(self, final: LSet) -> "LFiniteAutoma":
        if isinstance(None, final.type) and self.type != final.type:
            raise TypeError(f"To \"final\" expected set of elemets of type {self.type}, but gotted {final.type}")

        return LFiniteAutoma(NondeterministicFiniteAutomaton(states=copy(self.nfa.states), input_symbols=copy(self.nfa.symbols), start_state=copy(self.nfa.start_states), final_states=copy(self.nfa.final_states).union(final.set)))

    def starting(self) -> "LSet":
        return LSet({state.value for state in self.nfa.start_states})

    def final(self) -> "LSet":
        return LSet({state.value for state in self.nfa.final_states})

    def reachables(self) -> "LSet":
        result = set(LPair(state.value, state.value) for state in self.nfa.start_states.intersection(self.nfa.final_states))
        binary_matrix = build_binary_matrix_by_nfa(self.nfa)
        for node_from_index, node_to_index in zip(*transitive_closure(binary_matrix)):
            node_from = binary_matrix.states[node_from_index]
            node_to = binary_matrix.states[node_to_index]
            if node_from.is_start and node_to.is_final:
                result.add(LPair(node_from.value, node_to.value))

        return LSet(result)

    def marks(self) -> "LSet":
        return LSet({symbol.value for symbol in self.nfa.symbols})

    def edges(self) -> "LSet":
        return LSet({LTriple(state_from, mark, state_to) for state_from, items in self.nfa.to_dict().items()
        for mark, set_state_to in items.items()
        for state_to in (set_state_to if isinstance(set_state_to, set) else {set_state_to})})

    def nodes(self) -> "LSet":
        return LSet({state.value for state in self.nfa.symbols})

    def intersect(self, second: "LAutoma") -> "LFiniteAutoma":
        if self.type != second.type:
            raise TypeError("To \"intersect\" both arguments must be same type")
        if isinstance(second, LFiniteAutoma):
            return LFiniteAutoma(intersect_of_automata(self.nfa, second.nfa))
        else:
            return second.intersect(self)

    def union(self, second: "LAutoma") -> "LFiniteAutoma":
        if self.type != second.type:
            raise TypeError("To \"union\" both arguments must be same type")
        if isinstance(second, LFiniteAutoma):
            return LFiniteAutoma(self.nfa.union(second.nfa).to_deterministic(), self.type)
        else:
            return second.union(self)

    def concat(self, second: "LAutoma") -> "LFiniteAutoma":
        if self.type != second.type:
            raise TypeError("To \"concat\" both arguments must be same type")
        if isinstance(second, LFiniteAutoma):
            return LFiniteAutoma(self.nfa.concatenate(second.nfs).to_deterministic(), self.type)
        else:
            return second.concat(self)

    def star(self) -> "LFiniteAutoma":
        return LFiniteAutoma(self.nfa.kleene_star().to_deterministic())

    __repr__ = __str__