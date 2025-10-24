"""
VM Parser for the Hack VM language. See The Elements of Computing Systems chapter 7 for details.

Call with a --filename argument for the .vm file to parse. Defaults to the current directory
if the filename does not include a path.

VM files must have a .vm extension, and have the first letter of the filename capitalized in camelcase (e.g. FileName.vm).

Author: Will Henchy
Date: 2025-10-12
"""

import argparse
from dataclasses import dataclass
from textwrap import dedent
import os


@dataclass
class CommandTypes:
    """Dataclass containing the output string mappings of command types, to avoid typos and
    allow for quick reference. Not the most performant option but makes life easier."""

    push: str = "C_PUSH"
    pop: str = "C_POP"
    arithmetic: str = "C_ARITHMETIC"
    rtrn: str = "C_RETURN"
    function: str = "C_FUNCTION"
    call: str = "C_CALL"


@dataclass
class ParsedCommand:
    """Used for dot access to arg1/arg2 when iterating over the Parser object."""

    command_type: str
    arg1: str | None = None
    arg2: str | None = None


class Parser(object):
    """Parser for the Hack VM language. Requires a filename param on init (Parser(filename: str)).
    Iterate over lines with a for loop, accessing arg1 and arg2 with .arg1 and .arg2 and command_type
    with .command_type.

    Attributes:
        filename (str): The name of the file being parsed. Defaults to the current directory.
        lines (list[str]): A list of all lines in the file.
        has_more_lines (bool): Does the file have more lines to parse?
        current_line (int): The line number currently being parsed.
        total_lines (int): The total number of lines in the file.

    Iterable attributes:
        command_type (str): The current command's type. Types defined in the CommandTypes class.
        arg1 (str | None): The current line's arg1.
        arg2 (str | None): The current line's arg2.
    """

    filename: str
    lines: list[str] = list()
    current_line: int = -1  # Defaulting to -1 allows us to advance() before parsing, so we actually start on line 0 and also parse the final line.
    total_lines: int = 0
    _line_tokens: list[str]
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
    def _command_type(self):
        """The command type for the current line."""
        command_type: str | None = None
        token: str | None = None
        try:
            token = self._line_tokens[0]
            command_type = self._commands[token]
        except KeyError:
            raise ValueError(
                f"Unknown command at position 1 for line {self.current_line + 1}: {self._line_tokens}"
            )
        except IndexError:
            raise ValueError(
                f"Missing command type for command at position 1 for line {self.current_line + 1}: {self._line_tokens}; this should not happen and is likely a Parser bug."
            )
        if not command_type:
            raise ValueError(
                f"Missing command type for command {self._arg1_tokens[0]} at position 1 for line {self.current_line + 1}. This is likely a Parser bug."
            )
        return command_type

    @property
    def _arg1(self) -> str | None:
        """Return the first argument for the current command.
        If the command is a Return command, returns None instead."""
        try:
            if self._command_type == self._command_types.rtrn:
                return None
            elif self._command_type == self._command_types.arithmetic:
                return self._line_tokens[0]
            else:
                return self._line_tokens[1]
        except KeyError:
            raise ValueError(
                f"Error parsing command at position 2 on line {self.current_line + 1}: {self._line_tokens}"
            )
        except IndexError:
            raise ValueError(
                f"Missing argument for command at position 2 on line {self.current_line + 1}: {self._line_tokens}"
            )

    @property
    def _arg2(self) -> str | None:
        """Return the second argument for the current command if the command is a Push,
        Pop, Function, or Call command. Returns None otherwise."""
        try:
            if self._command_type in [
                self._command_types.push,
                self._command_types.pop,
                self._command_types.function,
                self._command_types.call,
            ]:
                return self._line_tokens[2]
            else:
                return None
        except KeyError:
            raise ValueError(
                f"Invalid command at position 3 on line {self.current_line + 1}: {self._line_tokens}"
            )
        except IndexError:
            raise ValueError(
                f"Missing argument for command at position 3 on line {self.current_line + 1}: {self._line_tokens}"
            )

    @property
    def _parsed_lines(self):
        """The full list of all parsed lines for the .vm file.
        Alternative private method to __iter__() in case the full parsed list is needed."""
        self._load_lines()
        parsed_args: list[ParsedCommand] = list()
        while self.has_more_lines:
            # current_line starts at -1 so we need to advance before parsing.
            # We advance() first to ensure that we parse the final line.
            self.advance()
            self._parse_line()
            parsed_args.append(
                ParsedCommand(self._command_type, self._arg1, self._arg2)
            )
        return parsed_args

    def _load_lines(self):
        """Load the lines of the file and prepare for parsing."""
        with open(self.filename, "r") as file:
            # Store the lines in a list, stripping out extra chars (indents, newlines, etc.).
            for line in file.readlines():
                stripped_line: str = dedent(line.strip())
                if (
                    len(stripped_line) > 0 and line[:2] != "//"
                ):  # Ignore blank lines and comments (lines that start with "//")
                    self.lines.append(stripped_line)
            self.lines = [dedent(line.strip()) for line in self.lines]
            self.total_lines = len(self.lines)

    def _parse_line(self):
        """Parse the current line and store the arg1 and arg2 tokens for access."""
        line: str = self.lines[self.current_line]
        tokens: list[str] = line.split(" ")
        self._line_tokens: list[str] = []
        self._arg1_tokens: list[str] = []
        self._arg2_tokens: list[str] = []
        for idx, t in enumerate(tokens):
            self._line_tokens.append(t)
            if idx > 2:
                raise ValueError(
                    f"Too many commands and arguments in line {self.current_line + 1}."
                )

    def advance(self):
        """Advance to the next non-empty non-comment line in the .vm file."""
        if self.has_more_lines:
            self.current_line += 1
            self._parse_line()
        else:
            raise IndexError("Cannot advance past the max line index.")

    def __init__(self, filename: str | None):
        if not filename:
            raise ValueError("No filename provided to Parser() init.")

        basename = os.path.basename(filename)  # Check against VM filename specs
        if ".vm" not in basename:
            raise ValueError("Filename must be a .vm file.")
        if basename[0].isupper() is False:
            raise ValueError(
                'Filename must begin with a capital letter (e.g. "FileName.vm").'
            )

        # Load and parse the vm file
        self.filename = filename
        self._load_lines()

    def __iter__(self):
        """Iterate over the lines in the .vm file.
        Yields a tuple of (ParsedCommand, list[str]) where the ParsedCommand is the parsed command"""
        while self.has_more_lines:
            # current_line starts at -1 so we need to advance before parsing.
            # We advance() first to ensure that we parse the final line.
            self.advance()
            self._parse_line()
            yield (
                ParsedCommand(self._command_type, self._arg1, self._arg2),
                self._line_tokens,
            )

    def __len__(self):
        return self.total_lines

    def __repr__(self):
        return f"Parser(filename={self.filename})"


if __name__ == "__main__":
    cli_parser = argparse.ArgumentParser(description="Hack VM parser.")
    cli_parser.add_argument(
        "filename",
        help="The name of the file to process",
    )
    args: argparse.Namespace = cli_parser.parse_args()
    filename: str = args.filename

    parser: Parser = Parser(filename)
    print(parser)
    for line, _ in parser:
        print(f"{line.command_type}: {line.arg1} {line.arg2}")
