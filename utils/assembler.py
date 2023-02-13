import os
import struct
import keystone
import argparse

class Assembler():
    """
    Assembler class, used to translate assembly code to binary
    """
    def __init__(self, arch, mode):
        self.arch = arch
        self.mode = mode
        self.ks = keystone.Ks(self.arch, self.mode)

    def assemble(self, code):
        """
        Assembles the given assembly code to binary and converts it to a byte array
        """
        # Assemble the code to binary
        encoding, count = self.ks.asm(code)    

        # Convert the binary to bytes
        bytes = struct.pack('B' * len(encoding), *encoding)

        return bytes
    
    def assemble_to_file(self, code, output_file):
        """
        Assembles the given assembly code to binary and writes it to a file
        """
        bytes = self.assemble(code)

        with open(output_file, "wb+") as file:
            file.write(bytes)

def main():
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Assemble MIPS assembly code to binary.')
    parser.add_argument('input_file', type=str, help='input assembly file name')
    parser.add_argument('-o', '--output-file', type=str, help='output file name (default is ./out.o)', default="./out.o")
    args = parser.parse_args()

    # Make sure the input file exists
    if (not os.path.exists(args.input_file)):
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
