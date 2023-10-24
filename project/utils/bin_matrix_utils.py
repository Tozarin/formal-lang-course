from collections import namedtuple

from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State
from scipy.sparse import (
    dok_matrix,
    kron,
    block_diag,
    lil_matrix,
    csc_matrix, csr_matrix,
    csr_array,
    lil_array,
    csc_array,
    dok_array,
    vstack,
)

BinaryMatrix = namedtuple(
    "BinaryMatrix", ["starting_states", "final_states", "indexes", "matrix"]
)


def build_binary_matrix_by_nfa(nfa: NondeterministicFiniteAutomaton, matrix_type: str) -> BinaryMatrix:

    """
    Builds decomposition of binary matrix by given nondeterministic automaton
    and together with other information wraps in tuple

    Args:
        nfa: nondeterministic automaton that would be base
        matrix_type: type of used matrix

    Returns:
        BinaryMatrix - namedtuple that contains starting states, final states,
        dictionary that mathes indexes of binnary matrix and numbers of states,
        decomposition of binary matrix
    """

    indexes = {state: index for index, state in enumerate(nfa.states)}

    matrix = dict()
    nfa_dict = nfa.to_dict()

    count_of_states = len(nfa.states)

    for mark in nfa.symbols:

        match matrix_type:
            case "lil":
                tmp_matrix = lil_matrix((count_of_states, count_of_states), dtype=bool)
            case "dok":
                tmp_matrix = dok_matrix((count_of_states, count_of_states), dtype=bool)
            case "csr":
                tmp_matrix = csr_matrix((count_of_states, count_of_states), dtype=bool)
            case "csc":
                tmp_matrix = csc_matrix((count_of_states, count_of_states), dtype=bool)

        for state_from, transitions in nfa_dict.items():
            states_to = set()
            if mark in transitions:
                state = transitions[mark]
                if isinstance(state, set):
                    states_to = state
                else:
                    states_to = {state}
            for state_to in states_to:
                tmp_matrix[
                    indexes[state_from],
                    indexes[state_to],
                ] = True
        matrix[mark] = tmp_matrix

    return BinaryMatrix(
        nfa.start_states,
        nfa.final_states,
        indexes,
        matrix,
    )


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
    indexes = bin_matrix.indexes

    nfa = NondeterministicFiniteAutomaton()

    for mark in matrix.keys():
        marked_array = matrix[mark].toarray()
        for i in range(len(marked_array)):
            for j in range(len(marked_array)):
                if marked_array[i][j]:
                    nfa.add_transition(indexes[State(i)], mark, indexes[State(j)])

    for starting_state in bin_matrix.starting_states:
        nfa.add_start_state(indexes[State(starting_state)])
    for final_state in bin_matrix.final_states:
        nfa.add_final_state(indexes[State(final_state)])

    return nfa


def transitive_closure(bin_matrix: BinaryMatrix, matrix_type: str) -> lil_matrix:

    """
    Calculates transitive closure of graph that is represented by binary matrix

    Args:
        bin_matrix: namedtuple with necessary information

    Returns:
        Transitive closure of graph
    """

    match matrix_type:
        case "lil":
            returned_matrix = lil_array((1, 1))
        case "dok":
            returned_matrix = dok_array((1, 1))
        case "csr":
            returned_matrix = csr_array((1, 1))
        case "csc":
            returned_matrix = csc_array((1, 1))

    if not bin_matrix.matrix.values():
        return returned_matrix

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


def intersect_of_automata_by_binary_matixes(
    left_bin_matrix: BinaryMatrix, right_bin_matrix: BinaryMatrix, matrix_type : str
) -> BinaryMatrix:

    """
    Calculates intersect of given automata represented as binary matixes

    Args:
        left_bin_matrix: left side matrix
        right_bin_matrix: right side matrix
        matrix_type: type of used matrix

    Returns:
        Binary matrix that represent intersect of automata
    """

    marks = left_bin_matrix.matrix.keys() & right_bin_matrix.matrix.keys()

    matrix = dict()
    starting_states = set()
    final_states = set()
    indexes = {}

    for mark in marks:
        matrix[mark] = kron(
            left_bin_matrix.matrix[mark],
            right_bin_matrix.matrix[mark],
            format=matrix_type,
        )

    for left_state, left_index in left_bin_matrix.indexes.items():
        for right_state, right_index in right_bin_matrix.indexes.items():
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

    return BinaryMatrix(starting_states, final_states, indexes, matrix)


def direct_sum(
    left_bin_matrix: BinaryMatrix,
    right_bin_matrix: BinaryMatrix,
    matrix_type: str,
) -> dict:

    """
    Direct sum of two binary matrixes that used marks of only left one

    Args:
        left_bin_matrix: left side matrix
        right_bin_matrix: right side matrix
        matrix_type: type of used matrix

    Returns:
        Dictionary where keys-marks matched with direct sums of corresponding matrixes
    """

    result_matrix = dict()
    size_of_right_matrix = len(right_bin_matrix.indexes)

    match matrix_type:
        case "lil":
            matrix_to_used = lil_matrix((size_of_right_matrix, size_of_right_matrix))
        case "dok":
            matrix_to_used = dok_matrix((size_of_right_matrix, size_of_right_matrix))
        case "csr":
            matrix_to_used = csr_matrix((size_of_right_matrix, size_of_right_matrix))
        case "csc":
            matrix_to_used = csc_matrix((size_of_right_matrix, size_of_right_matrix))

    for mark in left_bin_matrix.matrix.keys():
        
        match matrix_type:
            case "lil":
                result_matrix[mark] = lil_array( block_diag((left_bin_matrix.matrix[mark], (matrix_to_used if mark not in right_bin_matrix.matrix.keys() else right_bin_matrix.matrix[mark]))))
            case "dok":
                result_matrix[mark] = dok_array( block_diag((left_bin_matrix.matrix[mark], (matrix_to_used if mark not in right_bin_matrix.matrix.keys() else right_bin_matrix.matrix[mark]))))
            case "csr":
                result_matrix[mark] = csr_array( block_diag((left_bin_matrix.matrix[mark], (matrix_to_used if mark not in right_bin_matrix.matrix.keys() else right_bin_matrix.matrix[mark]))))
            case "csc":
                result_matrix[mark] = csc_array( block_diag((left_bin_matrix.matrix[mark], (matrix_to_used if mark not in right_bin_matrix.matrix.keys() else right_bin_matrix.matrix[mark]))))

    return result_matrix


def init_front(
    width: int,
    hight: int,
    indexes: dict,
    starting_states: set,
    starting_row: lil_array,
    matrix_type: str,
):

    """
    Initiates front matrix for bfs algorithm

    Args:
        width: width of front matrix
        hight: hight of front matrix
        indexes: indexes that matched with states of working matrix
        starting_states: states that algorithm start from
        starting_row: default values of working part of front
        matrix_type: type of used matrix

    Returns:
        Front matrix
    """

    match matrix_type:
        case "lil":
            front = lil_array((width, hight))
        case "dok":
            front = dok_array((width, hight))
        case "csr":
            front = csr_array((width, hight))
        case "csc":
            front = csc_array((width, hight))

    for state, index in indexes.items():
        if state in starting_states:
            front[index, index] = 1
            front[index, width:] = starting_row

    return front


def init_separeted_front(
    width: int,
    hight: int,
    indexes: dict,
    starting_states_for_fronts: set,
    graph_indexes: dict,
    starting_states: set,
    matrix_type: str,
):

    """
    Initiates front matrixes for separete variant of bfs algorithm

    Args:
        width: width of front matrix
        hight: hight of front matrix
        indexes: indexes that matched with states of working matrix
        starting_states_for_fronts: starting states for each front
        graph_indexes: indexes that matched with states of working graph
        starting_states: separeted states that algorithm start from
        matrix_type: type of used matrix

    Returns:
        Front matrixes that represented as one matrix with list of starting statesx
    """

    fronts = []
    list_of_starting_states = []

    for starting_state in starting_states:
        list_of_starting_states.append(starting_state)

        starting_row = [[int(starting_state == state) for state in graph_indexes.keys()]]

        match matrix_type:
            case "lil":
                starting_row_as_array = lil_array(starting_row)
            case "dok":
                starting_row_as_array = dok_array(starting_row)
            case "csr":
                starting_row_as_array = csr_array(starting_row)
            case "csc":
                starting_row_as_array = csc_array(starting_row)

        fronts.append(
            init_front(
                width,
                hight,
                indexes,
                starting_states_for_fronts,
                starting_row_as_array,
                matrix_type,
            )
        )

    match matrix_type:
        case "lil":
            returned_value = (lil_array(vstack(fronts)) if len(fronts) > 0 else lil_array((width, hight)), list_of_starting_states)
        case "dok":
            returned_value = (dok_array(vstack(fronts)) if len(fronts) > 0 else dok_array((width, hight)), list_of_starting_states)
        case "csr":
            returned_value = (csr_array(vstack(fronts)) if len(fronts) > 0 else csr_array((width, hight)), list_of_starting_states)
        case "csc":
            returned_value = (csc_array(vstack(fronts)) if len(fronts) > 0 else csc_array((width, hight)), list_of_starting_states)

    return returned_value
        


def sort_left_part_of_front(
    size_of_left_part: int,
    front: csr_array,
    matrix_type: str
):

    """
    Transport rows for each left part of front to get single matrixes

    Args:
        size_of_left_part: size of left part of front
        front: front
        matrix_type: type of used matrix

    Returns:
        Sorted front
    """

    match matrix_type:
        case "lil":
            new_front = lil_array(front.shape)
        case "dok":
            new_front = dok_array(front.shape)
        case "csr":
            new_front = csr_array(front.shape)
        case "csc":
            new_front = csc_array(front.shape)

    for i, j in zip(*front.nonzero()):
        if j < size_of_left_part:
            non_zero_row_right_of_row = front[[i]].tolil()[[0], size_of_left_part:]
            if non_zero_row_right_of_row.nnz > 0:
                row_shift = i // size_of_left_part
                new_front[row_shift + j, j] = 1
                new_front[
                    [row_shift + j], size_of_left_part:
                ] += non_zero_row_right_of_row

    return new_front
