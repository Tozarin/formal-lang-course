from collections import namedtuple
from pyformlang.finite_automaton import State
from scipy.sparse import dok_matrix, kron

BinaryMatrix = namedtuple(
    "BinaryMatrix", ["starting_states", "final_states", "indexes", "binary_matrix"]
)


class BinaryMatrixExepction(Exception):
    def __init__(self, msg: str):
        self.message = msg


def build_bm_by_nfa(nfa: NondeterministicFiniteAutomaton) -> BinaryMatrix:

    """
    Builds decomposition of binary matrix by given nondeterministic automaton
    and together with other information wraps in typle

    Args:
        nfa: nondeterministic automaton that would be base

    Returns:
        BinaryMatrix - namedtyple that contains starting states, final states,
        dictionary that mathes indexes of binnary matrix and numbers of states,
        decomposition of binary matrix
    """

    # state of automata, index of binary matrix
    indexes = {state: index for index, state in enumerate(nfa.states)}

    matrix = dict()
    nfa_dict = nfa.to_dict()

    count_of_marks = len(nfa.symbols)

    for mark in nfa.symbols:
        tmp_matrix = doc_matrix(count_of_marks, count_of_marks, dtype=Bool)

        """
            from  mark to    mark to
            0,    { a: 1, 2; b: 2 }
            1,    { c: 3, 4, ...}
        """
        for state_from, transitions in nfa_dict.items():
            states_to = set()
            for mark in transitions:
                states = transitions[mark]
                if isinstance(states, set):
                    states_to = states
                else:
                    states_to = {states}
                for state_to in states_to:
                    tmp_matrix[indexes[state_from], indexes[state_to]] = True
        matrix[mark] = tmp_matrix

    return BinaryMatrix(nfa.start_states, nfa.final_states, indexes, matrix)


def build_nfa_by_bm(bin_matrix: BinaryMatrix) -> NondeterministicFiniteAutomaton:

    """
    Builds nondeterministic automaton by given binary matrix

    Args:
        bin_matrix: namedtyple with necessary information

    Returns:
        Nondeterministic automaton
    """

    matrix = bin_matrix.binary_matrix
    indexes = binary_matrix.indexes

    nfa = NondeterministicFiniteAutomaton()

    for mark in matrix.keys():
        marked_array = matrix[mark].to_array()
        for i in range(len(marked_array)):
            for j in range(len(marked_array)):
                if marked_array[i][j]:
                    nfa.add_transition(indexes(State(i)), mark, indexes(State(j)))

    for starting_state in bin_matrix.starting_states:
        nfa.add_start_state(indexes(State(starting_state)))
    for final_state in bin_matrix.final_states:
        nfa.add_final_state(indexes(State(final_state)))

    return nfa


def transitive_closure(bin_matrix: BinaryMatrix) -> dok_matrix:

    """
    Calculates transitive closure of graph that is represented by binary matrix

    Args:
        bin_matrix: namedtyple with necessary information

    Returns:
        Transitive closure of graph
    """

    if not bin_matrix.matrix.values():
        raise BinaryMatrixExepction("Given binary matrix is empty")

    transitive_closure = sum(bin_matrix.matrix.values())

    prev_count_of_nonzero_elems = transitive_closure.count_nonzero()
    curr_count_of_nonzero_elems = 0

    while prev_count_of_nonzero_elems != curr_count_of_nonzero_elems:
        transitive_closure += transitive_closure @ transitive_closure
        prev_count_of_nonzero_elems, curr_count_of_nonzero_elems = (
            curr_count_of_nonzero_elems,
            transitive_closure.count_nonzero(),
        )

    return transitive_closure


def intersect_of_automata(
    left_nfa: NondeterministicFiniteAutomaton,
    right_nfa: NondeterministicFiniteAutomaton,
) -> NondeterministicFiniteAutomaton:

    """
    Calculates intersect of given automata

    Args:
        left_nfa: left side automaton
        right_nfa: right side automaton

    Returns:
        Intersect of automata
    """

    left_bin_matrix, right_bin_matrix = build_bm_by_nfa(left_nfa), build_bm_by_nfa(
        right_nfa
    )

    marks = left_bin_matrix.matrix.keys() & right_bin_matrix.matrix.keys()

    matrix = dict()
    starting_states = set()
    final_states = set()
    indexes = {}

    for mark in marks:
        matrix[mark] = kron(
            left_bin_matrix.matrix[mark], right_bin_matrix.matrix[mark], format="dok"
        )

    for left_state, left_index in left_bin_matrix.indexes:
        for right_state, right_index in right_bin_matrix.indexes:
            new_state = new_index = (
                left_index * len(right_bin_matrix.indexes) + right_index
            )
            indexes[new_state] = new_index

            if (
                left_state in left_bin_matrix.starting_states
                and right_state in right_bin_matrix.starting_states
            ):
                starting_states.add(new_state)
            if (
                left_state in left_bin_matrix.final_states
                and right_state in right_bin_matrix.final_states
            ):
                final_states.add(new_state)

    rez_bin_matrix = BinaryMatrix(starting_states, final_states, indexes, matrix)
    return build_nfa_by_bm(rez_bin_matrix)
