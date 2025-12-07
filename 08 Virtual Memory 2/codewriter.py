"""Nand2Tetris codewriter module for the Hack VM language.

Author: Will Henchy
Date: 2025-10-12
"""

import textwrap

import ram
from parser import CommandTypes, ParsedCommand, Parser


class CodeWriter(object):
    vm_filename: str
    output_filename: str
    _parser: Parser
    _command_types: CommandTypes = CommandTypes()
    _current_function: str | None = None
    _return_address: str | None = None

    def __init__(self, vm_filename: str, output_filename: str):
        print(
            f"Initializing CodeWriter with input file {vm_filename} and output file {output_filename}..."
        )
        self.output_filename = output_filename
        self.vm_filename = vm_filename
        self._parser = Parser(self.vm_filename)

    def _write_pushpop(self, command: ParsedCommand, line_number: int) -> str:
        """Writes the push and pop assembly commands to the output file.

        *Note:* Yes, we call textwrap.dedent() many times in this function, and it seems redundent. However, the multiple calls
        are necessary to fully de-indent the asm strings due to the varying levels of indentation used in the code here for readability.
        Yes, it is a perf issue and not ideal. However, given this is an academic exercise, we prioritize readability over performance.

        Args:
            command (ParsedCommand): The ParsedCommand object representing the current line in the .vm file.
            line_number (int): The line number of the current command in the .vm file.
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
        # Push assembly generation
        if command.command_type == self._command_types.push:
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
            elif command.arg1 in ["this", "that", "local", "argument"]:
                asm = f"""\
                @{base_memory_address} // Memory segment {command.arg1} at address {base_memory_address}
                D=M // Store the value of the base memory address (e.g. 300) into D
                @{memory_address_offset} //  Offset passed as arugment position three stored as a constant
                D=D+A // Offset the base memory address D by the constant value
                A=D // Access the address to read the value stored at (D+A)
                D=M // Store the value in D
                """
            elif command.arg1 == "pointer":
                asm = f"""\
                @{base_memory_address + memory_address_offset} // {command.arg1.title()} memory segment {command.arg1} at address {base_memory_address + memory_address_offset}
                D=M // Store the current value of the pointer in D
                """
            else:
                # Not implemented
                raise NotImplementedError(
                    f"Unimplimented {command.arg1} at line {line_number}."
                )

            # Remove indents from f-strings for readability
            asm = textwrap.dedent(asm)

            # Push logic is the same for all commands
            asm += textwrap.dedent("""\
            @SP // Proceed to push to the stack
            A=M // Address at the top of the stack
            M=D // Push the value in D to the stack memory location
            @SP // Stack pointer incriment begin
            M=M+1 // SP++
            """)
        # Pop assembly generation
        elif command.command_type == self._command_types.pop:
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
            else:
                raise NotImplementedError(
                    f"Unimplemented {command.arg1} at line {line_number}."
                )

            # Remove indents from f-strings for readability
            asm = textwrap.dedent(asm)

            # Generic push logic
            asm += textwrap.dedent("""\
            @R13 // R13 temporary register
            M=D // Store the offset address in R13
            @SP // Stack pointer
            M=M-1 // SP--
            A=M // Access the current top of the stack
            D=M // Get the value of the memory address at the top of the stack
            @R13 // Back to R13 so we can pop the value off the stack to the offset memory address
            A=M // Set our memory location to the offset address
            M=D // Store the value from the top of the stack to that offset address
            """)
        else:
            # Wtf? We should never get here.
            raise ValueError(
                f"Unknown command type passed to pushpop assembly generation function: {command.command_type}"
            )
        asm = textwrap.dedent(asm)

        if len(asm) == 0:
            raise ValueError(f"Invalid assembly code: {asm} at line {line_number}.")

        return asm

    def _write_arithmetic(self, command: ParsedCommand, line_number: int) -> str:
        """Writes the arithmetic assembly commands to the output file.
        Args:
            command (ParsedCommand): The ParsedCommand object representing the current line in the .vm file.
            line_number (int): The line number of the current command in the .vm file.
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
        elif vm_command == "eq":
            asm = f"""\
            @SP // Stack pointer
            M=M-1 // SP-- to value of y
            A=M // Load the memory value of y (M = address of y)
            D=M // Save the value of y in D
            @SP // Stack pointer
            M=M-1 // SP-- to value of x
            A=M
            M=M-D // Check for zero (equality) x = x - y
            D=M
            @EQUAL.{line_number} // Load the EQUAL memory address to A for the JEQ command if equal
            D;JEQ // Jump to the A address if D (x) is zero (the values are equal)
            (NOT_EQUAL.{line_number})
            D=0 // Twos compliment 00000000
            @END.{line_number} // Load the END address to jump an skip the EQUAL section
            0;JMP // Jump to the (END)
            (EQUAL.{line_number})
            D=-1 // Twos compliment 11111111
            (END.{line_number})
            @SP // Stack pointer
            A=M  // Get address for the memory location at the top of the stack
            M=D // Store the equality test to the top of the stack
            @SP // Stack pointer
            M=M+1 // SP++
            """
        elif vm_command == "gt":
            asm = f"""\
            @SP // Stack pointer
            M=M-1 // SP-- to value of y
            A=M // Load the memory value of y (M = address of y)
            D=M // Save the value of y in D
            @SP // Stack pointer
            M=M-1 // SP-- to value of x
            A=M // Load the value of x (M = address of x)
            M=M-D // x = x - y
            D=M // Store the result in D for a jump
            @GREATER.{line_number} // Load the GREATER memory address to A for the JGT command
            D;JGT // Jump to the A address if M (x) is greater than zero (the values are equal)
            (LESSER.{line_number})
            D=0 // Twos compliment 00000000
            @END.{line_number} // Load the END address to jump an skip the EQUAL section
            0;JMP // Jump to the (END)
            (GREATER.{line_number})
            D=-1 // Twos compliment 11111111
            (END.{line_number})
            @SP // Stack pointer
            A=M  // Get address for the memory location at the top of the stack
            M=D // Store the greater than test to the top of the stack
            @SP // Stack pointer
            M=M+1 // SP++
            """
        elif vm_command == "lt":
            asm = f"""\
            @SP // Stack pointer
            M=M-1 // SP-- to value of y
            A=M // Load the memory value of y (M = address of y)
            D=M // Save the value of y in D
            @SP // Stack pointer
            M=M-1 // SP-- to value of x
            A=M // Load the value of x (M = address of x)
            M=M-D // x = x - y
            D=M // Store the result in D for a jump
            @LESSER.{line_number} // Load the GREATER memory address to A for the JLT command
            D;JLT // Jump to the A address if M (x) is less than zero (the values are equal)
            (GREATER.{line_number})
            D=0 // Twos compliment 00000000
            @END.{line_number} // Load the END address to jump an skip the EQUAL section
            0;JMP // Jump to the (END)
            (LESSER.{line_number})
            D=-1 // Twos compliment 11111111
            (END.{line_number})
            @SP // Stack pointer
            A=M  // Get address for the memory location at the top of the stack
            M=D // Store the less than test to the top of the stack
            @SP // Stack pointer
            M=M+1 // SP++
            """
        elif vm_command == "and":
            asm = """\
            @SP // Stack pointer
            M=M-1 // SP-- to value of y
            A=M // Load the memory value of y (M = address of y)
            D=M // Save the value of y in D
            @SP // Stack pointer
            M=M-1 // SP-- to value of x
            A=M // Load the value of x (M = address of x)
            M=D&M // Bitwise AND stored to the stack location
            @SP // Stack pointer
            M=M+1 // SP++
            """
        elif vm_command == "or":
            asm = """\
            @SP // Stack pointer
            M=M-1 // SP-- to value of y
            A=M // Load the memory value of y (M = address of y)
            D=M // Save the value of y in D
            @SP // Stack pointer
            M=M-1 // SP-- to value of x
            A=M // Load the value of x (M = address of x)
            M=D|M // Bitwise OR stored to the stack location
            @SP // Stack pointer
            M=M+1 // SP++
            """
        elif vm_command == "not":
            asm = """\
            @SP // Stack pointer
            A=M-1 // Address one below the SP to get the value of y
            M=!M // y = negative y
            """
        else:
            raise NotImplementedError(
                f"Unimplemented arithmetic command: {vm_command} at line {line_number}u."
            )

        if len(asm) == 0:
            raise ValueError(f"Invalid assembly code: {asm} at line {line_number}.")

        return textwrap.dedent(
            asm
        )  # remove indentation in strings added for code readability

    def _label_string(self, command: ParsedCommand, line_number: int) -> str:
        """
        Creates a hack assembly label string based on the provided command and any function name
        if a function call was encountered prior to the label call (set at self._current_function).

        Used in functions that need to write a label that includes the current function name.

        Args:
            command (ParsedCommand): The ParsedCommand object representing the current line in the .vm file.
        """
        func: str | None = self._current_function
        name: str | None = command.arg1
        if not name:
            raise ValueError(f"Invalid label name: {name} at line {line_number}.")
        return textwrap.dedent(
            f"{func}${name}" if func else name
        )  # remove indentation in strings added for code readability

    def _write_label(self, command: ParsedCommand, line_number: int) -> str:
        """
        Writes the label command asm to the output file, with an optional function name
        if a function call was encountered prior to the label call.
        Args:
            command (ParsedCommand): The ParsedCommand object representing the current line in the .vm file.
            line_number (int): The line number of the current command in the .vm file.
        """
        return f"({self._label_string(command, line_number)}) // Label for {command.arg1}\n"

    def _write_goto(self, command: ParsedCommand, line_number: int) -> str:
        """
        Writes the goto command asm to the output file.
        Args:
            command (ParsedCommand): The ParsedCommand object representing the current line in the .vm file.
            line_number (int): The line number of the current command in the .vm file.
        """
        return textwrap.dedent(
            f"""\
            @{self._label_string(command, line_number)} // Get the label address for {command.arg1}
            0;JMP // Jump to the {command.arg1} label
            """
        )

    def _write_if_goto(self, command: ParsedCommand, line_number: int) -> str:
        """
        Writes the if-goto command asm to the output file.
        Args:
            command (ParsedCommand): The ParsedCommand object representing the current line in the .vm file.
            line_number (int): The line number of the current command in the .vm file.
        """
        return textwrap.dedent(
            f"""\
            @SP // Stack pointer to pop the top value for if-goto (jump if not zero)
            M=M-1 // Decrement stack pointer
            A=M // Load the address of the top value
            D=M // Load the value at the top of the stack
            @{self._label_string(command, line_number)} // Get the label address for {command.arg1}
            D;JNE // Jump to the {command.arg1} label if the value is not zero
            """
        )

    def _write_function(self, command: ParsedCommand, line_number: int) -> str:
        """
        Writes a function to the asm.
        Args:
            command (ParsedCommand): The ParsedCommand object representing the current line in the .vm file.
            line_number (int): The line number of the current command in the .vm file.
        """
        # Check if arg2 (nVars) exists before we proceed.
        if not command.arg2:
            raise ValueError(
                f"Error: Missing nVars for function {command.arg1} at line {line_number}"
            )

        asm: str = f"// Function {command.arg1}\n({command.arg1})\n"
        asm = textwrap.dedent(asm)
        try:
            nVars = int(command.arg2)
        except:
            raise ValueError(
                f"Error: Invalid nVars {command.arg2} for function command {command.arg1} at line {line_number}"
            )

        for a in range(nVars):
            asm += textwrap.dedent(f"""\
                // Set arg{a} to 0
                @0
                D=A
                @SP
                A=M
                M=D
                // Increment SP
                @SP
                M=M+1
            """)
        return asm

    def _write_call(self, command: ParsedCommand, line_number: int) -> str:
        """
        Writes the call command, saving the caller's frame and repositioning the stack pointer to begin
        the function call.
        Args:
            command (ParsedCommand): The ParsedCommand object representing the current line in the .vm file.
            line_number (int): The line number of the current command in the .vm file.
        """
        return_label: str = f"RETURN.{command.arg1}{command.arg2}{line_number}"
        asm: str = f"""\
            // Set up the return address for the function call {command.arg1}
            @({return_label}) // Push the return address onto the stack
            D=A
            @SP
            A=M
            M=D
            @SP // Increment the SP
            M=M+1
            // Save the caller's frame
            @{ram.NAMED_REGISTER_ADDRESSES["local"]} // LCL's base memory address
            D=M
            @SP
            A=M
            M=D // Push LCL's address on onto the stack
            @SP // Increment the SP
            M=M+1
            @{ram.NAMED_REGISTER_ADDRESSES["arguments"]} // ARG's base memory address
            D=M
            @SP
            A=M
            M=D // Push ARG's address on onto the stack
            @SP // Increment the SP
            M=M+1
            @{ram.NAMED_REGISTER_ADDRESSES["this"]} // THIS's base memory address
            D=M
            @SP
            A=M
            M=D // Push THIS's address on onto the stack
            @SP // Increment the SP
            M=M+1
            @{ram.NAMED_REGISTER_ADDRESSES["that"]} // THAT's base memory address
            D=M
            @SP
            A=M
            M=D // Push THAT's address on onto the stack
            @SP // Increment the SP
            M=M+1
            // Reposition ARG to SP - 5 - nargs
            @SP
            D=M
            @5
            D=D-A
            @{command.arg2}
            D=D-A
            @{ram.NAMED_REGISTER_ADDRESSES["arguments"]} // ARG's base memory address
            M=D
            // Reposition LCL to SP
            @SP
            A=M
            D=A
            @{ram.NAMED_REGISTER_ADDRESSES["local"]} // LCL's base address
            M=D
            // Call the function {command.arg2}
            @{self._label_string(command, line_number)} // Get the label address to call {command.arg2}
            0;JMP // Jump!
            // Mark our return address for the {command.arg2} function return
            ({return_label})  // Label for the return address
        """
        return textwrap.dedent(asm)

    def _write_return(self, command: ParsedCommand, line_number: int) -> str:
        asm = f"""\
        // Store the old local in R14
        @{ram.NAMED_REGISTER_ADDRESSES["local"]}
        D=M
        @{ram.NAMED_REGISTER_ADDRESSES["r14"]}
        M=D
        // R15 = *(endframe - 5)
        @{ram.NAMED_REGISTER_ADDRESSES["r15"]}
        M=D
        @5
        D=A
        @{ram.NAMED_REGISTER_ADDRESSES["r15"]}
        M=M-D
        A=M
        D=M
        @{ram.NAMED_REGISTER_ADDRESSES["r15"]}
        M=D
        // *ARG = pop()
        @SP
        M=M-1
        A=M
        D=M
        @{ram.NAMED_REGISTER_ADDRESSES["argument"]}
        A=M
        M=D
        // SP = ARG  + 1
        @{ram.NAMED_REGISTER_ADDRESSES["argument"]}
        D=M
        @SP
        M=D+1
        // Restore THAT
        @{ram.NAMED_REGISTER_ADDRESSES["r14"]}
        D=M
        @1
        A=D-A
        D=M
        @{ram.NAMED_REGISTER_ADDRESSES["that"]}
        M=D
        // Restore THIS
        @{ram.NAMED_REGISTER_ADDRESSES["r14"]}
        D=M
        @2
        A=D-A
        D=M
        @{ram.NAMED_REGISTER_ADDRESSES["this"]}
        M=D
        // Restore ARG
        @{ram.NAMED_REGISTER_ADDRESSES["r14"]}
        D=M
        @3
        A=D-A
        D=M
        @{ram.NAMED_REGISTER_ADDRESSES["argument"]}
        M=D
        // Restore LCL
        @{ram.NAMED_REGISTER_ADDRESSES["r14"]}
        D=M
        @4
        A=D-A
        D=M
        @{ram.NAMED_REGISTER_ADDRESSES["local"]}
        M=D
        // Return to caller
        @{ram.NAMED_REGISTER_ADDRESSES["r15"]}
        A=M
        0;JMP
        """
        return textwrap.dedent(asm)

    def write(self, debug: bool = True):
        """Writes the entire .vm file to the output file.
        Args:
            debug (bool): If True, include VM tokens as comments in the output file.
        """
        print(f"Parsing {self.vm_filename}...")

        line_count: int = 0
        with open(self.output_filename, "w") as file:
            file.write(
                f"// {self.vm_filename.split('/')[-1]} translated to the Hack assembly language from the book The Elements of Computing systems using the Interpres translator.\n// Interpres by Will Henchy, 2025.\n\n"
            )  # Include the filename in the output file (and split out any path information)
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
                elif line.command_type == self._command_types.label:
                    file.write(self._write_label(line, line_count))
                elif line.command_type == self._command_types.goto:
                    file.write(self._write_goto(line, line_count))
                elif line.command_type == self._command_types.if_goto:
                    file.write(self._write_if_goto(line, line_count))
                elif line.command_type == self._command_types.function:
                    file.write(self._write_function(line, line_count))
                elif line.command_type == self._command_types.call:
                    file.write(self._write_call(line, line_count))
                elif line.command_type == self._command_types._return:
                    file.write(self._write_return(line, line_count))
                else:
                    file.write(f"{line.command_type}: {line.arg1} {line.arg2}\n")
                if debug:
                    file.write("\n")  # Extra whitespace for readability
                line_count += 1

        print(f"Successfully wrote {line_count} lines to {self.output_filename}.")
