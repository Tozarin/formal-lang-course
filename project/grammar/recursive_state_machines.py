from collections import namedtuple
from pathlib import Path

from project.grammar.extended_contex_free_grammar import (
    ExtendedContexFreeGrammar,
    extended_contex_free_grammar_from_string,
    extended_contex_free_grammar_from_file,
)

RecursiveStateMachine = namedtuple(
    "RecursiveStateMachine", ["starting_symbol", "subautomatons"]
)


def recursive_state_machine_from_extended_contex_free_grammar(
    extended_contex_free_grammar: ExtendedContexFreeGrammar | Path | str,
    starting_symbol: str,
) -> RecursiveStateMachine:

    """
    Builds recursive state machine from given extended contex free grammar

    Args:
        extended_contex_free_grammar: extended contex free grammar to
        be sourse represented as namedtuple or string or path to file with grammar
        starting_symbol: starting nonterminal to builded grammar

    Returns:
        Recursive state machine equivalent given grammar
    """

    if isinstance(extended_contex_free_grammar, Path):
        extended_contex_free_grammar = extended_contex_free_grammar_from_file(
            extended_contex_free_grammar, starting_symbol
        )

    if isinstance(extended_contex_free_grammar, str):
        extended_contex_free_grammar = extended_contex_free_grammar_from_string(
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

    """
    Minimizes given recursive state machine

    Args:
        recursive_state_machine: recursive state machine to
        be minimized

    Returns:
        Minimize recursive state machine
    """

    for nonterminal, subautomata in recursive_state_machine.subautomatons.items():
        recursive_state_machine.subautomatons[nonterminal] = subautomata.minimize()

    return recursive_state_machine
