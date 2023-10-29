from collections import namedtuple
from itertools import product

from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State
from scipy.sparse import (
    dok_matrix,
    kron,
    dok_array,
    csr_array,
    lil_array,
    vstack,
    bmat,
)

StateInfo = namedtuple("StateInfo", ["value", "is_start", "is_final"])

BinaryMatrix = namedtuple("BinaryMatrix", ["states", "matrix"])


def build_binary_matrix_by_nfa(nfa: NondeterministicFiniteAutomaton) -> BinaryMatrix:

    """
    Builds decomposition of binary matrix by given nondeterministic automaton
    and together with other information wraps in tuple

    Args:
        nfa: nondeterministic automaton that would be base

    Returns:
        BinaryMatrix - namedtuple that contains states and
        decomposition of binary matrix
    """

    states = list(
        StateInfo(state.value, state in nfa.start_states, state in nfa.final_states)
        for state in nfa.states
    )
    count_of_states = len(states)
    transitions = nfa.to_dict()
    matrixes = {}

    for node_from in transitions:
        for mark, nodes_to in transitions[node_from].items():
            matrix = matrixes.setdefault(
                mark.value, dok_array((count_of_states, count_of_states), dtype=bool)
            )
            index_from = next(
                index for index, state in enumerate(states) if state.value == node_from
            )
            for node_to in nodes_to if isinstance(nodes_to, set) else {nodes_to}:
                index_to = next(
                    index
                    for index, state in enumerate(states)
                    if state.value == node_to
                )
                matrix[index_from, index_to] = True

    for key in matrixes:
        matrixes[key] = matrixes[key].tocsr()

    return BinaryMatrix(states, matrixes)


def build_nfa_by_binary_matrix(
    bin_matrix: BinaryMatrix,
) -> NondeterministicFiniteAutomaton:

    """
    Builds nondeterministic automaton by given binary matrix

    Args:
        bin_matrix: namedtuple with necessary information

    Returns:
        Nondeterministic automaton
    """

    matrix = bin_matrix.matrix
    nfa = NondeterministicFiniteAutomaton()

    for mark in matrix.keys():
        marked_array = matrix[mark].toarray()
        for i in range(len(marked_array)):
            for j in range(len(marked_array)):
                if marked_array[i][j]:
                    nfa.add_transition(
                        State(bin_matrix.states[i].value),
                        mark,
                        State(bin_matrix.states[j].value),
                    )

    for state in bin_matrix.states:
        if state.is_start:
            nfa.add_start_state(State(state.value))
        if state.is_final:
            nfa.add_final_state(State(state.value))

    return nfa


def transitive_closure(bin_matrix: BinaryMatrix) -> tuple:

    """
    Calculates transitive closure of graph that is represented by binary matrix

    Args:
        bin_matrix: namedtuple with necessary information

    Returns:
        Transitive closure of graph
    """

    count_of_states = len(bin_matrix.states)
    transitive_closure = sum(
        bin_matrix.matrix.values(),
        start=csr_array((count_of_states, count_of_states), dtype=bool),
    )
    transitive_closure.eliminate_zeros()

    while True:
        prev_count_of_nonzero_elems = transitive_closure.nnz

        transitive_closure += transitive_closure @ transitive_closure

        if prev_count_of_nonzero_elems == transitive_closure.nnz:
            break

    return transitive_closure.nonzero()


def intersect_of_automata_by_binary_matixes(
    left_bin_matrix: BinaryMatrix, right_bin_matrix: BinaryMatrix
) -> BinaryMatrix:

    """
    Calculates intersect of given automata represented as binary matixes

    Args:
        left_bin_matrix: left side matrix
        right_bin_matrix: right side matrix

    Returns:
        Binary matrix that represent intersect of automata
    """

    states = [
        StateInfo(
            (left_state.value, right_state.value),
            left_state.is_start and right_state.is_start,
            left_state.is_final and right_state.is_final,
        )
        for left_state, right_state in product(
            left_bin_matrix.states, right_bin_matrix.states
        )
    ]

    count_of_states = len(states)
    matrixes = {}

    for mark in set(left_bin_matrix.matrix.keys()).union(
        set(right_bin_matrix.matrix.keys())
    ):
        if mark in left_bin_matrix.matrix and mark in right_bin_matrix.matrix:
            matrixes[mark] = csr_array(
                kron(
                    left_bin_matrix.matrix[mark],
                    right_bin_matrix.matrix[mark],
                    format="csr",
                )
            )
        else:
            matrixes[mark] = csr_array((count_of_states, count_of_states), dtype=bool)

    return BinaryMatrix(states, matrixes)


def direct_sum(
    left_bin_matrix: BinaryMatrix,
    right_bin_matrix: BinaryMatrix,
) -> dict:

    """
    Direct sum of two binary matrixes that used marks of only left one

    Args:
        left_bin_matrix: left side matrix
        right_bin_matrix: right side matrix

    Returns:
        Dictionary where keys-marks matched with direct sums of corresponding matrixes
    """

    states = left_bin_matrix.states + right_bin_matrix.states
    matrixes = dict()

    for mark in set(left_bin_matrix.matrix.keys()).intersection(
        set(right_bin_matrix.matrix.keys())
    ):
        matrixes[mark] = csr_array(
            bmat(
                [
                    [left_bin_matrix.matrix[mark], None],
                    [None, right_bin_matrix.matrix[mark]],
                ]
            )
        )

    return BinaryMatrix(states, matrixes)


def init_front(
    states_of_graph: list,
    states_of_request: list,
    starting_row: lil_array,
) -> csr_array:

    """
    Initiates front matrix for bfs algorithm

    Args:
        states_of_graph: states of used graph
        states_of_request: states of used request
        starting_row: default values of working part of front

    Returns:
        Front matrix
    """

    width = len(states_of_request)
    hight = len(states_of_request) + len(states_of_graph)
    front = lil_array((width, hight))

    for index, state in enumerate(states_of_request):
        if state.is_start:
            front[index, index] = True
            front[index, width:] = starting_row

    return front.tocsr()


def init_separeted_front(
    states_of_graph: list,
    states_of_request: list,
    starting_indexes: list,
) -> csr_array:

    """
    Initiates front matrixes for separete variant of bfs algorithm

    Args:
        states_of_graph: states of used graph
        states_of_request: states of used request
        starting_indexes: indexes of starting states

    Returns:
        Front matrixes that represented as one matrix with list of starting statesx
    """

    width = len(states_of_request)
    hight = len(states_of_graph)

    fronts = [
        init_front(
            states_of_graph,
            states_of_request,
            lil_array([index == starting_index for index in range(hight)], dtype=bool),
        )
        for starting_index in starting_indexes
    ]

    return (
        csr_array(vstack(fronts))
        if len(fronts)
        else csr_array((width, hight + hight), dtype=bool)
    )


def sort_left_part_of_front(
    size_of_left_part: int,
    front: csr_array,
) -> csr_array:

    """
    Transport rows for each left part of front to get single matrixes

    Args:
        size_of_left_part: size of left part of front
        front: front

    Returns:
        Sorted front
    """

    new_front = lil_array(front.shape, dtype=bool)

    for i, j in zip(*front.nonzero()):
        if j < size_of_left_part:
            non_zero_row_right_of_row = front[[i]].tolil()[[0], size_of_left_part:]
            if non_zero_row_right_of_row.nnz > 0:
                row_shift = i // size_of_left_part
                new_front[row_shift + j, j] = True
                new_front[
                    [row_shift + j], size_of_left_part:
                ] += non_zero_row_right_of_row

    return new_front.tocsr()
