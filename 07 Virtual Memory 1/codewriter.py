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

from parser import Parser, ParsedCommand, CommandTypes
import ram


class CodeWriter(object):
    vm_filename: str
    output_filename: str
    _parser: Parser
    _command_types: CommandTypes = CommandTypes()

    def __init__(self, vm_filename: str, output_filename: str):
        print(
            f"Initializing CodeWriter with input file {vm_filename} and output file {output_filename}..."
        )
        self.output_filename = output_filename
        self.vm_filename = vm_filename
        self._parser = Parser(self.vm_filename)

    def _write_pushpop(self, command: ParsedCommand) -> str:
        """Writes the push and pop assembly commands to the output file.
        Args:
            command (ParsedCommand): The ParsedCommand object representing the current line in the .vm file.
        """
        asm: str = ""
        pointer_name: str = ram.NAMED_REGISTER_NAMES[str(command.arg1)]
        value: str | None = command.arg2
        if command.command_type == self._command_types.push:
            asm += f"@{value}\nD=A\n"  # Store the value in the D register
            asm += f"@{pointer_name}\nA=M\nM=D\n"  # Push the D register value onto the relevant stack
            asm += f"@{pointer_name}\nM=M+1\n"  # Increment the stack pointer
        elif command.command_type == self._command_types.pop:
            asm += f"@{pointer_name}\nM=M-1\n"  # Decrement the stack pointer value
            asm += f"@{pointer_name}\nD=M\n"  # Read the value from the top of the stack and store in the D register
        else:
            raise ValueError(
                f"Unknown command type for pushpop command: {command.command_type}"
            )
        return asm

    def _write_arithmetic(self, command: ParsedCommand):
        """Writes the arithmetic assembly commands to the output file.
        Args:
            command (ParsedCommand): The ParsedCommand object representing the current line in the .vm file.
        """
        # TODO:
        pass

    def write(self, debug=False):
        """Writes the entire .vm file to the output file.
        Args:
            debug (bool): If True, include VM tokens as comments in the output file.
        """
        print(f"Parsing {self.vm_filename}...")
        line_count: int = 0
        with open(self.output_filename, "w") as file:
            for line, token_list in self._parser:
                if debug:  # Include VM tokens as a comment for debugging if requested.
                    file.write(f"//{' '.join(token_list)}\n")
                if (
                    line.command_type == self._command_types.push
                    or line.command_type == self._command_types.pop
                ):
                    file.write(self._write_pushpop(line))
                else:
                    file.write(f"{line.command_type}: {line.arg1} {line.arg2}\n")
                line_count += 1
        print(f"Successfully wrote {line_count} lines to {self.output_filename}.")
