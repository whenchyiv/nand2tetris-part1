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
import textwrap


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

    def _generate_push_asm(self, pointer: str) -> str:
        """Generic push command generation for re-use."""
        return asm

    def _generate_pop_asm(self, pointer: str) -> str:
        """Generic pop command generation for re-use."""
        return asm

    def _write_pushpop(self, command: ParsedCommand, line_number: int) -> str:
        """Writes the push and pop assembly commands to the output file.
        Args:
            command (ParsedCommand): The ParsedCommand object representing the current line in the .vm file.
        """
        try:
            base_memory_address: int = ram.NAMED_REGISTER_ADDRESSES[
                str(command.arg1)
            ]  # Get the base memory address for the memory segment
        except KeyError:
            raise ValueError(f"Invalid memory segment at line {line_number}.")
        arg2_value: str | None = (
            command.arg2
        )  # Get the string value of the segment offset
        if not arg2_value:
            raise ValueError(
                f"Push command missing memory address at line {line_number}."
            )
        memory_address_offset: int = int(
            arg2_value
        )  # Convert to int for pointer arithmetic

        asm: str = ""
        if command.command_type == self._command_types.push:
            # Push assembly generation
            asm = f"""\
            @{base_memory_address + memory_address_offset} // Memory segment {command.arg1} at address {base_memory_address} plus offset of {memory_address_offset}
            D=M //  Store the value in the D register for addition to the stack
            @SP // Stack pointer
            A=M // Get current address for the top of the stack
            M=D // Store the D value at the top of the stack
            @SP // Stack pointer
            M=M+1 // SP++
            """
        elif command.command_type == self._command_types.pop:
            # Pop assembly generation
            asm = f"""\
            @SP // Stack pointer
            M=M-1 // SP--
            A=M // Get current address for the top of the stack
            D=M // Store the value in the D register for addition to the stack
            @{base_memory_address + memory_address_offset} // Memory segment {command.arg1} at address {base_memory_address} plus offset of {memory_address_offset}
            M=D // Store the D value at the top of the stack
            """
        else:
            # Wtf? We should never get here.
            raise ValueError(
                f"Unknown command type passed to pushpop assembly generation function: {command.command_type}"
            )

        return textwrap.dedent(
            asm
        )  # remove indentation in strings added for code readability

    def _write_arithmetic(self, command: ParsedCommand, line_number: int) -> str:
        """Writes the arithmetic assembly commands to the output file.
        Args:
            command (ParsedCommand): The ParsedCommand object representing the current line in the .vm file.
        """
        vm_command: str | None = command.arg1
        if not vm_command:
            raise ValueError(
                f"Missing command for arithmetic command at line {line_number}."
            )

        asm: str = ""
        if vm_command == "add":
            asm = """\
            @SP // Stack pointer
            M=M-1 // SP-- to value of y
            A=M // Load the memory value of y (M = address of y)
            D=M // D register = y 
            @SP // Stack pointer
            M=M-1 //SP-- to value of  x
            A=M // Load the memory value of x (M = address of x)
            M=M+D // M (x) = M (x) + D (y)
            @SP // Stack pointer
            M=M+1 // SP++
            """
        elif vm_command == "sub":
            asm = """\
            @SP // Stack pointer
            M=M-1 // SP-- to value of y
            A=M // Load the memory value of y (M = address of y)
            D=M // D register = y 
            @SP // Stack pointer
            M=M-1 //SP-- to value of  x
            A=M // Load the memory value of x (M = address of x)
            M=M-D // M (x) = M (x) - D (y)
            @SP // Stack pointer
            M=M+1 // SP++
            """
        elif vm_command == "neg":
            asm = """\
            @SP // Stack pointer
            A=M-1 // Address one below the SP to get the value of y
            M=-M // y = negative y
            """
        else:
            asm = f"""// Unimplemented arithmetic command: {vm_command}"""

        return textwrap.dedent(
            asm
        )  # remove indentation in strings added for code readability

    def write(self, debug: bool = True):
        """Writes the entire .vm file to the output file.
        Args:
            debug (bool): If True, include VM tokens as comments in the output file.
        """
        print(f"Parsing {self.vm_filename}...")

        line_count: int = 0
        with open(self.output_filename, "w") as file:
            for line, token_list in self._parser:
                if debug:  # Include VM tokens as a comment for debugging if requested via the debug var.
                    file.write(f"//{' '.join(token_list)}\n")
                if (
                    line.command_type == self._command_types.push
                    or line.command_type == self._command_types.pop
                ):
                    file.write(self._write_pushpop(line, line_count))
                elif line.command_type == self._command_types.arithmetic:
                    file.write(self._write_arithmetic(line, line_count))
                else:
                    file.write(f"{line.command_type}: {line.arg1} {line.arg2}\n")
                if debug:
                    file.write("\n")  # Extra whitespace for readability
                line_count += 1

        print(f"Successfully wrote {line_count} lines to {self.output_filename}.")
