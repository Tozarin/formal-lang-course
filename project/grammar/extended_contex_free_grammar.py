from pathlib import Path
from collections import namedtuple
from re import split

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


def extend_contex_free_grammar_from_string(
    extend_contex_free_grammar: str, starting_symbol: str
) -> ExtendedContexFreeGrammar:

    string_productions = extend_contex_free_grammar.split("\n")

    productions: dict[Variable, Regex] = {}
    nonterminals = {}
    terminals = {}
    for production in string_productions:
        tokens = production.split(" ")

        if len(tokens) < 3:
            raise ExtendedContexFreeGrammarExepction("Production missing elements")

        if tokens[1] not in ["->"]:
            raise ExtendedContexFreeGrammarExepction("Missing -> in production")

        for symbol in split("[]|+?()*", " ".join(tokens[2:])):
            terminals.add(symbol)

        nonterminal = tokens[0]
        subautomata = Regex(" ".join(tokens[2:]))

        productions[nonterminal] = subautomata
        nonterminals.add(nonterminal)

    terminals = list(map(lambda x: Value(x), terminals - nonterminals))
    nonterminals = list(map(lambda x: Value(x)), nonterminals)

    return ExtendedContexFreeGrammar(
        nonterminals, terminals, Value(starting_symbol), productions
    )


def extend_contex_free_grammar_from_file(
    path_to_file_with_grammar: Path, starting_symbol: str
) -> ExtendedContexFreeGrammar:

    with open(path_to_file_with_grammar, "r") as file:
        grammar = file.read()

    return extend_contex_free_grammar_from_string(grammar, starting_symbol)
