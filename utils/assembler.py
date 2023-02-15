"""
This file contains the Assembler class which uses Keystone to turn assembly code into binary
"""
import os
import struct
import argparse
from typing import Tuple
import keystone

class Assembler():
    """
    Assembler class, used to translate assembly code to binary
    """
    def __init__(self, arch: int, mode: int):
        self.arch = arch
        self.mode = mode
        self.ks = keystone.Ks(self.arch, self.mode)

    def assemble(self, code: str) -> Tuple[bytes, int]:
        """
        Assembles the given assembly code to binary and converts it to a byte array
        """
        # Assemble the code to binary
        encoding, count = self.ks.asm(code)

        # Convert the binary to bytes
        byte_string = struct.pack('B' * len(encoding), *encoding)

        return byte_string, count

    def assemble_to_file(self, code: str, output_file: str) -> None:
        """
        Assembles the given assembly code to binary and writes it to a file
        """
        machine_code_bytes = self.assemble(code)

        with open(output_file, "wb+") as file:
            file.write(machine_code_bytes)

def main():
    """
    Main function, calls the assembler with the given arguments
    """
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Assemble MIPS assembly code to binary.')
    parser.add_argument('input_file', type=str, help='input assembly file name')
    parser.add_argument('-o', '--output-file', type=str, help='output file name (default is ./out.o)', default="./out.o")
    args = parser.parse_args()

    # Make sure the input file exists
    if not os.path.exists(args.input_file):
        print("Usage: python assembler.py [input_file] [-o output_file]")
        return

    # Init the assembler
    assembler = Assembler(keystone.KS_ARCH_MIPS, keystone.KS_MODE_MIPS32 + keystone.KS_MODE_LITTLE_ENDIAN)

    # Assemble the code to file
    code = ""
    with open (args.input_file, "r") as file:
        code = file.read()

    assembler.assemble_to_file(code, args.output_file)

if __name__ == "__main__":
    main()
