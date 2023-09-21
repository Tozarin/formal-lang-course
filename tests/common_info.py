path_to_results = "tests/results/"
path_to_automata = path_to_results + "automata/"
path_to_graphs = path_to_results + "graphs/"

reg_test = [
    ("", "blanck_fin_automata.dot"),
    ("a", "a_fin_automata.dot"),
    ("a*", "multy_a_fin_automata.dot"),
    ("a|b", "a_or_b_fin_automata.dot"),
    (r"\|", "vertical_line_fin_automata.dot"),
    (r"\.", "dot_fin_automata.dot"),
    (r"\+", "plus_fin_automata.dot"),
    (r"\*", "asterisk_fin_automata.dot"),
    (r"\(", "left_parent_fin_automata.dot"),
    (r"\)", "right_parent_fin_automata.dot"),
    (r"\$", "epsilon_fin_automata.dot"),
]

gen_auto_from_graph_test = ["graph_to_gen_automata.dot", "empty_graph.dot"]

nondeterministic_automata_for_build_test = [
    ([(0, "b", 0), (0, "a", 1), (1, "b", 1), (1, "a", 0)], [0], [1]),
    (
        [(0, "b", 0), (0, "a", 1), (1, "b", 1), (1, "a", 0), (0, "c", 1), (1, "d", 0)],
        [0],
        [1],
    ),
    ([(0, "b", 0), (0, "a", 1), (1, "a", 1), (1, "b", 0), (0, "c", 1)], [0], [0, 1]),
]

transitive_closure_test = [
    ([(0, "b", 0), (0, "a", 1), (1, "b", 1), (1, "a", 0)], [0], [1], [[1, 1], [1, 1]]),
    ([(0, "a", 1), (1, "b", 0)], [0], [1, 2], [[1, 1, 0], [1, 1, 0], [0, 0, 0]]),
]

# first_cycle, second_cycle, (first_cycle_mark, second_cycle_mark), regular_expression, starting_states, finale_states, expected_output
regular_request_test = [
    (
        3,
        2,
        ("a", "b"),
        "a*|b",
        {},
        {},
        [
            [0, 1],
            [1, 2],
            [0, 4],
            [2, 1],
            [3, 1],
            [0, 2],
            [2, 2],
            [1, 0],
            [3, 2],
            [1, 3],
            [0, 0],
            [1, 1],
            [0, 3],
            [2, 0],
            [3, 0],
            [2, 3],
            [4, 5],
            [3, 3],
            [5, 0],
        ],
    ),
    (3, 2, ("a", "b"), "x*|y", [], [], []),
    (
        3,
        2,
        ("a", "b"),
        "a*|y",
        {},
        {},
        [
            [0, 0],
            [0, 1],
            [0, 2],
            [0, 3],
            [1, 0],
            [1, 1],
            [1, 2],
            [1, 3],
            [2, 0],
            [2, 1],
            [2, 2],
            [2, 3],
            [3, 0],
            [3, 1],
            [3, 2],
            [3, 3],
        ],
    ),
    (3, 2, ("a", "b"), "a*|b", {0}, {1, 2, 3, 4}, [[0, 1], [0, 2], [0, 3], [0, 4]]),
    (3, 2, ("a", "b"), "a*|b", {4}, {4, 5}, [[4, 5]]),
    (3, 2, ("a", "b"), "b", {0}, {0, 1, 2, 3}, []),
    (3, 2, ("a", "b"), "b", {0}, {4, 5}, [[0, 5], [0, 4]]),
    (3, 2, ("a", "b"), "", {0}, {4, 5}, []),
]
