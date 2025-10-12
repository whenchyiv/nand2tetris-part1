import linecache


class HackParser(object):
    current_line: str = ""
    line_number: int = 0

    def __init__(self, filename: str = None):
        self.filename = filename
        if ".asm" not in self.filename:
            raise ValueError("File must be .asm file.")
        self._current_line_number = 0
        with open(filename, 'r') as f:
            self.linecount = len([1 for _ in f])
            print(self.linecount)
        self.advance()

    @property
    def has_more_lines(self):
        return self._current_line_number <= self.linecount

    def advance(self):
        line = ""
        while len(line) < 1:
            self._current_line_number += 1
            if self.has_more_lines:
                l = linecache.getline(
                    self.filename,
                    self._current_line_number
                )
                line = l.split("//")[0].replace(" ", "").replace("\n", "")
            else:
                raise IndexError("End of file.")
                break
        self.current_line = line
        if self.instruction_type != "L_INSTRUCTION":
            self.line_number += 1

    @property
    def instruction_type(self):
        if self.current_line.startswith("@"):
            return "A_INSTRUCTION"
        elif self.current_line.startswith("("):
            return "L_INSTRUCTION"
        else:
            return "C_INSTRUCTION"

    @property
    def symbol(self):
        if (
            self.instruction_type == "A_INSTRUCTION" or
            self.instruction_type == "L_INSTRUCTION"
        ):
            return self.current_line.replace(
                "@",
                ""
            ).replace(
                "(",
                ""
            ).replace(
                ")",
                ""
            )
        else:
            return ""

    @property
    def dest(self):
        if self.instruction_type == "C_INSTRUCTION":
            if "=" in self.current_line:
                return self.current_line.split("=")[0]
            else:
                return "null"
        else:
            return ""

    @property
    def jump(self):
        if self.instruction_type == "C_INSTRUCTION":
            if ";" in self.current_line:
                return self.current_line.split(";")[1]
            else:
                return "null"
        else:
            return ""

    @property
    def comp(self):
        if self.instruction_type == "C_INSTRUCTION":
            comp_inst = self.current_line
            if ";" in self.current_line:
                comp_inst = self.current_line.split(";")[0]
            if "=" in self.current_line:
                return self.current_line.split("=")[1]
            return comp_inst
        else:
            return ""

    @property
    def a_value(self):
        if self.instruction_type == "C_INSTRUCTION":
            if "M" in self.comp:
                return "1"
            else:
                return "0"
        else:
            return ""
