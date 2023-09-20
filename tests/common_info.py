path_to_results = "tests/results/"
path_to_automata = path_to_results + "automata/"
path_to_graphs = path_to_results + "graphs/"

reg_test = [
    ("", "blanck_fin_automata.dot"),
    ("a", "a_fin_automata.dot"),
    ("a*", "multy_a_fin_automata.dot"),
    ("a|b", "a_or_b_fin_automata.dot"),
    ("\|", "vertical_line_fin_automata.dot"),
]

gen_auto_from_graph_test = ["graph_to_gen_automata.dot", "empty_graph.dot"]
