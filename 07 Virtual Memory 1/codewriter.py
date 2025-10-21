"""Nand2Tetris codewriter module for the Hack VM language.

Author: Will Henchy
Date: 2025-10-12
"""

"""
# Plan:
- Initialize with a Parser() and filename
- write() function which:
    - opens the file
    - iterates over the parser
    - calls to the write_arithmetic and write_pushpop commands to write each line of assembly code based on the command type provided by the line
    - closes the file and saves to the given filename
    - returns success and a status message (wrote blah blah blah)

# Psuedocode:
class CodeWriter:
    filename: str
    parser: Parser
    
    __init__()
    _write_pushpop()
    _write_arithmetic()
    write()
"""

from parser import Parser


class CodeWriter(object):
    vm_filename: str
    output_filename: str
    _parser: Parser

    def __init__(self, vm_filename: str, output_filename: str):
        print(
            f"Initializing CodeWriter with input file {vm_filename} and output file {output_filename}..."
        )
        self.output_filename = output_filename
        self.vm_filename = vm_filename
        self._parser = Parser(self.vm_filename)

    def _write_pushpop(self):
        # TODO:
        pass

    def _write_arithmetic(self):
        # TODO:
        pass

    def write(self):
        print(f"Parsing {self.vm_filename}...")
        line_count: int = 0
        with open(self.output_filename, "w") as file:
            for line in self._parser:
                file.write(f"{line.command_type}: {line.arg1} {line.arg2}\n")
                line_count += 1
        print(f"Successfully wrote {line_count} lines to {self.output_filename}.")
