import argparse
from dataclasses import dataclass
from textwrap import dedent


@dataclass
class CommandTypes:
    """Dataclass containing string mappings of command types to avoid typos and
    allow for quick reference."""

    push: str = "C_PUSH"
    pop: str = "C_POP"
    arithmetic: str = "C_ARITHMETIC"


class Parser(object):
    """Parser for the Hack VM language. Requires a filename param on init (Parser(filename='')).
    Attributes:
        filename (str): The name of the file being parsed. Defaults to the current directory.
        lines (list[str]): A list of all lines in the file.
        command_type (str): The current command's type. Types defined in the CommandTypes class.
        arg1 (str): The current line's arg1.
        arg2 (str): The current line's arg2.
        has_more_lines (bool): Does the file have more lines to parse?
        current_line (int): The line number currently being parsed.
        total_lines (int): The total number of lines in the file.
    """

    filename: str
    lines: list[str]
    command_type: str
    current_line: int = 0
    total_lines: int = 0
    _arg1_tokens: list[str]
    _arg2_tokens: list[str]
    _command_types: CommandTypes = CommandTypes()
    _commands: dict[str, str] = {
        "push": _command_types.push,
        "pop": _command_types.pop,
        "add": _command_types.arithmetic,
        "sub": _command_types.arithmetic,
        "neg": _command_types.arithmetic,
        "eq": _command_types.arithmetic,
        "gt": _command_types.arithmetic,
        "lt": _command_types.arithmetic,
        "and": _command_types.arithmetic,
        "or": _command_types.arithmetic,
        "not": _command_types.arithmetic,
    }

    @property
    def has_more_lines(self):
        """Does the file have more lines to parse?"""
        if self.current_line + 1 < self.total_lines:
            return True
        else:
            return False

    @property
    def arg1(self):
        try:
            return self._commands[self._arg1_tokens[0]]
        except KeyError:
            raise ValueError(
                f"Unknown command {self._arg1_tokens[0]} at position 1 for line {self.current_line + 1}."
            )

    @property
    def arg2(self):
        try:
            return self._commands[self._arg2_tokens[0]]
        except KeyError:
            raise ValueError(
                f"Invalid command {self._arg2_tokens[0]} at position 2 for line {self.current_line + 1}."
            )

    def __init__(self, filename: str | None):
        if not filename:
            raise ValueError("No filename provided to Parser() init.")

        # Check against VM filename specs
        if ".vm" not in filename:
            raise ValueError("Filename must be a .vm file.")
        if filename[0].isupper() is False:
            raise ValueError(
                'Filename must begin with a capital letter (e.g. "FileName.vm").'
            )

        # Load and parse the vm file
        self.filename = filename
        self._load_lines()

    def _load_lines(self):
        """Load the lines of the file and prepare for parsing."""
        with open(self.filename, "r") as file:
            # Store the lines in a list, stripping out extra chars (indents, newlines, etc.).
            self.lines = [dedent(line.strip()) for line in file.readlines()]
            self.total_lines = len(self.lines)

    def _parse_line(self):
        """Parse the current line and store the arg1 and arg2 tokens for access."""
        line: str = self.lines[self.current_line]
        tokens: list[str] = line.split(" ")
        self._arg1_tokens: list[str] = []
        self._arg2_tokens: list[str] = []
        for idx, t in enumerate(tokens):
            if idx == 0:
                self._arg1_tokens.append(t)
            else:
                if idx > 2:
                    raise ValueError(
                        f"Too many commands and arguments in line {self.current_line + 1}."
                    )
                self._arg2_tokens.append(t)

    def advance(self):
        if self.has_more_lines:
            self.current_line += 1
            self._parse_line()
        else:
            raise IndexError("Cannot advance past the max line index.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hack VM parser.")
    parser.add_argument("filename", help="The name of the file to process")
    args = parser.parse_args()
    filename = args.filename

    with open(filename, "r") as file:
        print(file)
