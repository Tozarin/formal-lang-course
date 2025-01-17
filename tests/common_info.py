path_to_results = "tests/results/"
path_to_automata = path_to_results + "automata/"
path_to_graphs = path_to_results + "graphs/"
path_to_bfs_test_graphs = path_to_graphs + "bfs_regular_request/"
path_to_grammars = path_to_results + "grammars/"
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
        {
            (0, 1),
            (1, 2),
            (0, 4),
            (2, 1),
            (3, 1),
            (0, 2),
            (2, 2),
            (1, 0),
            (3, 2),
            (1, 3),
            (0, 0),
            (1, 1),
            (0, 3),
            (2, 0),
            (3, 0),
            (2, 3),
            (4, 5),
            (3, 3),
            (5, 0),
        },
    ),
    (3, 2, ("a", "b"), "x*|y", {}, {}, set()),
    (
        3,
        2,
        ("a", "b"),
        "a*|y",
        {},
        {},
        {
            (0, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (1, 0),
            (1, 1),
            (1, 2),
            (1, 3),
            (2, 0),
            (2, 1),
            (2, 2),
            (2, 3),
            (3, 0),
            (3, 1),
            (3, 2),
            (3, 3),
        },
    ),
    (3, 2, ("a", "b"), "a*|b", {0}, {1, 2, 3, 4}, {(0, 1), (0, 2), (0, 3), (0, 4)}),
    (3, 2, ("a", "b"), "a*|b", {4}, {4, 5}, {(4, 5)}),
    (3, 2, ("a", "b"), "b", {0}, {0, 1, 2, 3}, set()),
    (3, 2, ("a", "b"), "b", {0}, {4}, {(0, 4)}),
    (3, 2, ("a", "b"), "", {0}, {4, 5}, set()),
]

# name_of_graph, regular_expression, starting_states, finale_states, separated_variant_expected_output, non_separated_variant_expected_output
bfs_regular_request_test = [
    ("first.dot", "a*", {"1"}, {}, set(), set()),
    ("second.dot", "a*", {"1"}, {"1"}, {("1", "1")}, {"1"}),
    ("third.dot", "a*", {"1"}, {"1"}, set(), set()),
    ("fourth.dot", "a*", {"1"}, {"2", "3"}, {("1", "2"), ("1", "3")}, {"2", "3"}),
    ("fifth.dot", "a*c", {"1"}, {}, {("1", "3"), ("1", "4")}, {"3", "4"}),
]

contex_free_and_weak_chomsky_forms = [
    ("", None, "", None),
    ("S -> a", None, "", None),
    ("S -> a", "S", "S -> a", "S"),
    ("A -> a", "A", "A -> a", "A"),
    ("S -> a", "B", "", "B"),
    ("S -> A B\nA -> a\nB -> b", "S", "S -> A B\nA -> a\nB -> b", "S"),
    ("S -> A S | ending\nA -> a", "S", "S -> A S | ending\nA -> a", "S"),
    (
        "S -> A B | ending\nA -> B S\nB -> b",
        "S",
        "S -> A B | ending\nA -> B S\nB -> b",
        "S",
    ),
    ("S -> epsilon", "S", "S -> epsilon", "S"),
    ("S -> A B\nA -> a\nB -> epsilon", "S", "S -> A B\nA -> a\nB -> epsilon", "S"),
    (
        "S -> A B C D E\nA -> a\nB -> b\nC -> c\nD -> d\nE -> e",
        "S",
        "S -> A C#CNF#1\nC#CNF#1 -> B C#CNF#2\nC#CNF#2 -> C C#CNF#3\nC#CNF#3 -> D E\nA -> a\nB -> b\nC -> c\nD -> d\nE -> e",
        "S",
    ),
    (
        "S -> a b c d e",
        "S",
        'S -> "VAR:a#CNF#" C#CNF#1\nC#CNF#1 -> "VAR:b#CNF#" C#CNF#2\nC#CNF#2 -> "VAR:c#CNF#" C#CNF#3\nC#CNF#3 -> "VAR:d#CNF#" "VAR:e#CNF#"\na#CNF# -> a\nb#CNF# -> b\nc#CNF# -> c\nd#CNF# -> d\ne#CNF# -> e',
        "S",
    ),
    (
        "S -> a b c epsilon",
        "S",
        'S -> "VAR:a#CNF#" C#CNF#1\nC#CNF#1 -> "VAR:b#CNF#" "VAR:c#CNF#"\na#CNF# -> a\nb#CNF# -> b\nc#CNF# -> c',
        "S",
    ),
    (
        "S -> a B c\nB -> b",
        "S",
        'S -> "VAR:a#CNF#" C#CNF#1\nC#CNF#1 -> B "VAR:c#CNF#"\na#CNF# -> a\nB -> b\nc#CNF# -> c',
        "S",
    ),
    ("S -> A\nA -> B\nB -> b", "S", "S -> b", "S"),
    (
        "S -> a B C | epsilon\nB -> E b\nE -> epsilon\nC -> B | c F\n F -> E",
        "S",
        'S -> "VAR:a#CNF#" C#CNF#1 | epsilon\nC#CNF#1 -> B C\nB -> E "VAR:b#CNF#"\nE -> epsilon\nC -> E "VAR:b#CNF#" | "VAR:c#CNF#" F\nF -> epsilon\na#CNF# -> a\nb#CNF# -> b\nc#CNF# -> c',
        "S",
    ),
]

names_of_grammar_files = [
    ("first.grammar", "S", "S -> a", "S"),
    ("second.grammar", "A", "A -> a", "A"),
    ("third.grammar", "B", "S -> a", "B"),
    ("fourth.grammar", "S", "S -> A B\nA -> a\nB -> b", "S"),
    ("fifth.grammar", "S", "S -> A S | ending\nA -> a", "S"),
    ("sixth.grammar", "S", "S -> epsilon", "S"),
]

common_starting_symbol = "S"

extended_grammars = [
    ("S -> a", ["S"], ["a"], {"S": "a"}),
    ("S -> a b S", ["S"], ["a", "b"], {"S": "a b"}),
    ("S -> a N\nN -> b", ["S", "N"], ["a", "b"], {"S": "a", "N": "b"}),
    ("S -> epsilon", ["S"], [], {"S": ""}),
    ("S -> endpoint", ["S"], [], {"S": ""}),
    ("S -> [a b]", ["S"], ["a", "b"], {"S": "[a b]"}),
]
