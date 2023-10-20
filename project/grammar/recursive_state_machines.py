from collections import namedtuple
from pathlib import Path

from project.grammar.extended_contex_free_grammar import (
    ExtendedContexFreeGrammar,
    extend_contex_free_grammar_from_string,
    extend_contex_free_grammar_from_file,
)

RecursiveStateMachine = namedtuple(
    "RecursiveStateMachine", ["starting_symbol", "subautomatons"]
)


def recursive_state_machine_from_extended_contex_free_grammar(
    extended_contex_free_grammar: ExtendedContexFreeGrammar | Path | str,
    starting_symbol: str,
) -> RecursiveStateMachine:

    if isinstance(extended_contex_free_grammar, Path):
        extended_contex_free_grammar = extend_contex_free_grammar_from_file(
            extend_contex_free_grammar, starting_symbol
        )

    if isinstance(extended_contex_free_grammar, str):
        extended_contex_free_grammar = extend_contex_free_grammar_from_file(
            extended_contex_free_grammar, starting_symbol
        )

    return RecursiveStateMachine(
        extended_contex_free_grammar.starting_symbol,
        {
            nonterminal: subautomata.to_epsilon_nfa()
            for nonterminal, subautomata in extended_contex_free_grammar.productions.items()
        },
    )


def minimize_recursive_state_machine(
    recursive_state_machine: RecursiveStateMachine,
) -> RecursiveStateMachine:

    for nonterminal, subautomata in recursive_state_machine.subautomatons.items():
        recursive_state_machine.subautomatons[nonterminal] = subautomata.minimize()

    return recursive_state_machine
