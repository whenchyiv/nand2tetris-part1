"""Nand2Tetris interpreter module for the Hack VM language.

Author: Will Henchy
Date: 2025-10-12
"""

from codewriter import CodeWriter
import argparse


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Nand2Tetris virtual machine language translator."
    )
    arg_parser.add_argument(
        "-i",
        "--input",
        help="Required. The name of the vm file to process. Must be CamelCase and end in .vm (e.g. ProgFile.vm).",
        required=True,
    )
    arg_parser.add_argument(
        "-o",
        "--output",
        help="Optional. The name of the file to output the assembly code to. Must be CamelCase and end in .asm extension. Default: Prog.asm.",
        default="Prog.asm",
    )

    args = arg_parser.parse_args()

    if args.output:
        if not args.output.endswith(".asm") or not args.output[0].isupper():
            arg_parser.error(
                "Output filename must be a .asm file and begin with an uppercase letter (e.g. FileName.asm)."
            )

    code_writer = CodeWriter(args.input, args.output)
    code_writer.write()
