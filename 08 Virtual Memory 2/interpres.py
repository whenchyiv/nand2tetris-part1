"""Nand2Tetris VM translator for the Hack VM language.

Author: Will Henchy
Date: 2025-10-12
"""

from codewriter import CodeWriter
import argparse
import os


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Nand2Tetris virtual machine language translator."
    )
    arg_parser.add_argument(
        "-i",
        "--input",
        help="Required. The name of the vm file to process. Must be CamelCase and end in .vm (e.g. ProgFile.vm).",
    )
    arg_parser.add_argument(
        "-o",
        "--output",
        help="Optional. The name of the file to output the assembly code to. Must be CamelCase and end in .asm extension. Default: Prog.asm.",
        default="Prog.asm",
    )
    arg_parser.add_argument(
        "-d",
        "--debug",
        help="Optional. Include VM tokens as comments in the output file. Default: False.",
        action="store_true",
        default=False,
    )

    args = arg_parser.parse_args()

    if args.output:
        basename = os.path.basename(args.output)  # Check against VM filename specs
        if not basename.endswith(".asm") or not basename[0].isupper():
            arg_parser.error(
                "Output filename must be a .asm file and begin with an uppercase letter (e.g. FileName.asm)."
            )

    is_directory = os.path.isdir(args.input)
    code_writer = CodeWriter(args.output)
    if not is_directory:
        code_writer.set_filename(args.input)
        code_writer.write(debug=args.debug)
    else:
        for idx, filename in enumerate(os.listdir(args.input)):
            write_bootstrap = idx == 0  # Only write the bootstrap code once
            if filename.endswith(".vm"):
                file_path = f"{args.input}/{filename}"
                code_writer.set_filename(file_path)
                code_writer.write(write_bootstrap=write_bootstrap, debug=args.debug)
