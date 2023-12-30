import argparse
from hackparser import HackParser
from translator import generate_binary_codes


SYMBOLTABLE = {
    "R0": "0",
    "R1": "1",
    "R2": "2",
    "R3": "3",
    "R4": "4",
    "R5": "5",
    "R6": "6",
    "R7": "7",
    "R8": "8",
    "R9": "9",
    "R10": "10",
    "R11": "11",
    "R12": "12",
    "R13": "13",
    "R14": "14",
    "R15": "15",
    "SP": "0",
    "LCL": "1",
    "ARG": "2",
    "THIS": "3",
    "THAT": "4",
    "SCREEN": "16384",
    "KBD": "24576"
}

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Hack assembler.")
    argparser.add_argument("-f", "--file", required=True, help=".asm file")
    argparser.add_argument("-o", "--output", required=True, help="Output filename (.hack)")
    args = argparser.parse_args()
    if ".hack" not in args.output:
        raise ValueError("Output must be .hack file.")

    # FIRST PASS (ADD L_INSTRUCTIONS TO SYMBOL TABLE)
    print(f"Scanning {args.file}...")

    symbol_parser = HackParser(filename=args.file)
    while symbol_parser.has_more_lines:
        labels = []
        if symbol_parser.instruction_type == "L_INSTRUCTION":
            if symbol_parser.symbol not in labels:
                SYMBOLTABLE[symbol_parser.symbol] = str(
                    symbol_parser.line_number
                )
                labels.append(symbol_parser.symbol)
        try:
            symbol_parser.advance()
        except Exception as e:
            print(e)
            break

    print(f"LABELS: {labels}")
    print(SYMBOLTABLE)

    parser = HackParser(filename=args.file)
    binary = list()
    var_address = 16

    # SECOND PASS (ASSEMBLY)
    print(f"Assembling {args.file}...")

    while parser.has_more_lines:
        print(f"Assembling line {parser.current_line}")
        if parser.instruction_type == "C_INSTRUCTION":
            bin_codes = generate_binary_codes(parser)
            print(bin_codes)
            line_binary = f"111{bin_codes['a']}{bin_codes['comp']}{bin_codes['dest']}{bin_codes['jump']}"
        elif parser.instruction_type == "A_INSTRUCTION":
            if (
                not SYMBOLTABLE.get(parser.symbol) and
                not parser.symbol[0].isdigit()
            ):
                print(f"Storing var {parser.symbol}")
                SYMBOLTABLE[parser.symbol] = str(var_address)
                var_address += 1
            line_binary = f"0{format(int(SYMBOLTABLE.get(parser.symbol, parser.symbol)), '015b')}"
        if parser.instruction_type != "L_INSTRUCTION":
            print(line_binary)
            binary.append(line_binary)
        try:
            parser.advance()
        except Exception as e:
            print(e)
            break

    with open(args.output, "w") as f:
        for l in binary:
            f.write(f"{l}\n")

    print(f"Saved {args.output}")
