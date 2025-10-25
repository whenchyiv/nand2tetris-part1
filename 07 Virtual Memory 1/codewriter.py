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
            if command.arg1 == "constant":
                asm = f"""\
                @{command.arg2} // Constant value
                D=A // Store the value of the constant in D
                """
            elif command.arg1 in ["static", "temp"]:
                asm = f"""\
                @{base_memory_address + memory_address_offset} // {command.arg1.title()} memory segment {command.arg1} at address {base_memory_address + memory_address_offset}
                D=M // Store the value in D
                """
            elif command.arg1 == "pointer":
                asm = f"""\
                @{base_memory_address + memory_address_offset} // {command.arg1.title()} memory segment {command.arg1} at address {base_memory_address + memory_address_offset}
                D=M // Store the current value of the pointer in D
                """
            elif command.arg1 in ["this", "that", "local", "argument"]:
                asm = f"""\
                @{base_memory_address} // Memory segment {command.arg1} at address {base_memory_address}
                D=M // Store the value of the base memory address (e.g. 300) into D
                @{memory_address_offset} //  Offset passed as arugment position three stored as a constant
                D=D+A // Offset the base memory address D by the constant value
                A=D // Access the address to read the value stored at (D+A)
                D=M // Store the value in D
                """
            else:
                # Not implemented
                raise NotImplementedError(
                    f"Unimplimented {command.arg1} at line {line_number}."
                )
            # Push logic is the same for all commands
            asm += """\
            @SP // Proceed to push to the stack
            A=M // Address at the top of the stack
            M=D // Push the value in D to the stack memory location
            @SP // Stack pointer incriment begin
            M=M+1 // SP++
            """
        elif command.command_type == self._command_types.pop:
            # Pop assembly generation
            if command.arg1 in ["static", "temp"]:
                asm = f"""\
                @{base_memory_address + memory_address_offset} // {command.arg1.title()} memory segment {command.arg1} at address {base_memory_address + memory_address_offset}
                D=A // Store the value in D
                """
            elif command.arg1 in ["this", "that", "local", "argument"]:
                asm = f"""\
                @{base_memory_address} // Memory segment {command.arg1} at address {base_memory_address}
                D=M // Store the value of the base memory address (e.g. 300) into D
                @{memory_address_offset} //  Offset passed as arugment position three stored as a constant
                D=D+A // Offset the base memory address D by the constant value
                """
            elif command.arg1 == "pointer":
                asm = f"""\
                @{base_memory_address + memory_address_offset} // {command.arg1.title()} memory segment {command.arg1} at address {base_memory_address + memory_address_offset}
                D=A // Set the D value to the current value of the pointer
                """
            # Generic push logic
            asm += """\
            @R13 // R13 temporary register
            M=D // Store the offset address in R13
            @SP // Stack pointer
            M=M-1 // SP--
            A=M // Access the current top of the stack
            D=M // Get the value of the memory address at the top of the stack
            @R13 // Back to R13 so we can pop the value off the stack to the offset memory address
            A=M // Set our memory location to the offset address
            M=D // Store the value from the top of the stack to that offset address
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
            M=D+M // M (x) = M (x) + D (y)
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
