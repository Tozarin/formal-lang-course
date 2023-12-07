from dataclasses import dataclass

from project.interpret.types import LPair, LTriple

@dataclass
class Pattern:
    pass

@dataclass
class PAny(Pattern):
    pass

@dataclass
class PName(Pattern):
    name: str

@dataclass
class PPair(Pattern):
    first: Pattern
    second: Pattern

@dataclass
class PTriple(Pattern):
    starting: Pattern
    mark: PAny | PName
    final: Pattern

def match(pattern: Pattern, value) -> dict:
    match[pattern, value]:
        case [PAny(), _]:
            return {}
        case [PName(name), _]:
            return {name: value}
        case [PPair(first, second), elem]:
            first_matched = match(first, elem[0])
            second_matched = match(second, elem[1])
            return first_matched | second_matched
        case [PTriple(starting, mark, final), elem]:
            starting_matched = match(starting, elem[0])
            mark_matched = match(mark, elem[1])
            final_matched = match(final, elem[2])
            return starting_matched | mark_matched | final_matched
        case _:
            raise ValueError(f"Vant match pattern {pattern} with value {value}")