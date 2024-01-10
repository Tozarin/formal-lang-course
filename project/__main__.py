from sys import argv
from pathlib import Path

from project.interpret.interpret import from_file

try:
    from_file(Path(argv[1]))
except RuntimeError as e:
    exit(e)
