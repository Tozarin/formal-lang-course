from pathlib import Path
from collections import namedtuple

from pyformlang.cfg import CFG, Variable
from pyformlang.regular_expression import Regex

from project.utils.grammar_utils import read_contex_free_grammar_from_file

ExtendedContexFreeGrammar = namedtuple(
    "ExtendedContexFreeGrammar",
    ["nonterminals", "terminals", "starting_symbol", "productions"],
)


class ExtendedContexFreeGrammarExepction(Exception):
    def __init__(self, msg: str):
        self.message = msg


def extend_contex_free_grammar(
    contex_free_grammar: CFG | str | Path, starting_nonterminal: str = None
) -> ExtendedContexFreeGrammar:

    """
    Converts contex free grammar to extended variant

    Args:
        gracontex_free_grammarph: contex free grammar represented
        as CFG or string or path to file with grammar
        starting_nonterminal: starting nonterminal to converted grammar

    Returns:
        Extended contex free grammar equivalent given one
    """

    if isinstance(contex_free_grammar, str):
        contex_free_grammar = CFG.from_text(
            contex_free_grammar, Variable(starting_nonterminal)
        )

    if isinstance(contex_free_grammar, str):
        contex_free_grammar = read_contex_free_grammar_from_file(
            contex_free_grammar, starting_nonterminal
        )

    starting_symbol = (
        contex_free_grammar.start_symbol
        if contex_free_grammar.starting_symbol is not None
        else Variable("S")
    )
    nonterminals = set(contex_free_grammar.nonterminals)
    nonterminals.add(starting_symbol)

    productions: dict[Variable, Regex] = {}
    for production in contex_free_grammar.productions:
        subautomata = Regex(
            " ".join(symbol.value for symbol in production.body)
            if len(production.body > 0)
            else "$"
        )

        productions[production.head] = (
            productions[production.head].union(subautomata)
            if production.head in productions
            else subautomata
        )

    return ExtendedContexFreeGrammar(
        nonterminals, set(contex_free_grammar.terminals), starting_symbol, productions
    )


def extended_contex_free_grammar_from_string(
    extend_contex_free_grammar: str, starting_symbol: str
) -> ExtendedContexFreeGrammar:

    """
    Builds extended contex free grammar from string representation

    Args:
        extend_contex_free_grammar: extended contex free grammar
        reprsented as string
        starting_symbol: starting nonterminal to builed grammar

    Returns:
        Extended contex free grammar as namedtuple
    """

    string_productions = extend_contex_free_grammar.split("\n")

    productions: dict[Variable, Regex] = {}
    nonterminals = set()
    terminals = set()
    for production in string_productions:
        tokens = production.split(" ")

        if len(tokens) < 3:
            raise ExtendedContexFreeGrammarExepction("Production missing elements")

        if tokens[1] not in ["->"]:
            raise ExtendedContexFreeGrammarExepction("Missing -> in production")

        for token in tokens[2:]:
            token = filter(lambda char: char not in "[]()|+*?" ,token)
            for symbol in token:
                terminals.add(symbol)

        nonterminal = tokens[0]
        subautomata = Regex(" ".join(tokens[2:]))

        productions[nonterminal] = subautomata
        nonterminals.add(nonterminal)

    terminals = list(map(lambda symbol: Variable(symbol), terminals - nonterminals))
    nonterminals = list(map(lambda symbol: Variable(symbol), nonterminals))

    return ExtendedContexFreeGrammar(
        nonterminals, terminals, Variable(starting_symbol), productions
    )


def extended_contex_free_grammar_from_file(
    path_to_file_with_grammar: Path, starting_symbol: str
) -> ExtendedContexFreeGrammar:

    """
    Reads extended contex free grammar from file

    Args:
        path_to_file_with_grammar: path to file with
        extended contex free grammar
        starting_symbol: starting nonterminal to readed grammar

    Returns:
        Extended contex free grammar as namedtuple
    """

    with open(path_to_file_with_grammar, "r") as file:
        grammar = file.read().trim()

    return extend_contex_free_grammar_from_string(grammar, starting_symbol)
