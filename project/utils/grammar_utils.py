from pathlib import Path

from pyformlang.cfg import CFG, Variable

def contex_free_to_weak_chomsky_form(contex_free_grammar: str | CFG, start_nonterminal: str = "S") -> CFG:

    """
    Converts contex free grammar is reprsented as string or CFG 
    to equivalent weak Chomsky form

    Args:
        contex_free_grammar: contex free grammar to be converted
        start_nonterminal: starting nonterminal for new grammar

    Returns:
        Equivalent grammar that represented in weak Chomsky form
    """

    if not isinstance(contex_free_grammar, CFG):
        contex_free_grammar = CFG.from_text(contex_free_grammar, Variable(start_nonterminal))
        
    contex_free_grammar = contex_free_grammar.remove_useless_symbols().eliminate_unit_productions().remove_useless_symbols()
    productions_to_decompose = contex_free_grammar._get_productions_with_only_single_terminals()
    contex_free_grammar = contex_free_grammar._decompose_productions(productions_to_decompose)

    return CFG(start_symbol=contex_free_grammar._start_symbol, productions=set(contex_free_grammar))

def read_contex_free_grammar_from_file(path_to_grammar: Path, start_nonterminal: str = "S") -> CFG:

    """
    Reads contex free grammar from file

    Args:
        path_to_grammar: path to file that contained grammar
        start_nonterminal: starting nonterminal for grammar

    Returns:
        Readed grammar
    """
    
    with open(path_to_grammar, "r") as file:
        grammar = file.read()

    return CFG.from_text(grammar, Variable(start_nonterminal))
