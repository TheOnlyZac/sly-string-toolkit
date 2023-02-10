import os, argparse, keystone, struct;
from generator import strings, trampoline, pnach;
from datetime import datetime

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate PNACH file from CSV.')
    parser.add_argument('-i', '--input', type=str, help='the input CSV file name (default is strings.csv)', default="strings.csv")
    parser.add_argument('-o', '--output', type=str, help='the output file name (default is ./out/07652DD9.mod.pnach)', default="./out/07652DD9.mod.pnach")
    parser.add_argument('-a', '--address', type=str, help='address to write the strings to (default is 0x203C7980)', default="203C7980")
    parser.add_argument('-v', '--verbose', action='store_true', help='show verbose output')
    parser.add_argument('-d', '--debug', action='store_true', help='output asm and bin files for debugging')
    args = parser.parse_args()

    # Check if the input file was specified, and if not, if strings.csv exists
    if (args.input == "strings.csv" and not os.path.exists(args.input)):
        print("Error: strings.csv not found.")
        print("Please specify an input file using the -i flag.")
        return
    
    # Create the out folder if it doesn't exist
    if (not os.path.exists("./out")):
        if (args.verbose):
            print("Creating out folder...")
        os.mkdir("./out")

    # 1 - Generate the strings pnach and populate string pointers
    print("Reading strings from csv...")
    strings_obj = strings.Strings(args.input, int(args.address, 16))
    strings_pnach, string_pointers = strings_obj.gen_pnach()

    # Print string pointers if verbose
    if (args.verbose):
        print("String pointers:")
        for string_id, string_ptr in string_pointers:
            print(f"ID: {hex(string_id)} | Ptr: {hex(string_ptr)}")
        print("Strings pnach:")
        print(strings_pnach)

    # 2 - Generate the mod assembly code
    print("Generating assembly code...")
    trampoline_obj = trampoline.Trampoline(string_pointers)
    mips_code = trampoline_obj.gen_asm()
    
    # Print assembly code if verbose
    if (args.verbose):
        print("Assembly code:")
        print(mips_code)
    
    # Write assembly code to file if debug
    if (args.debug):
        print("Writing assembly code to file...")
        with open("./out/mod.asm", "w+") as file:
            file.write(mips_code)

    # 3 - Assemble the asm code to binary
    print("Assembling asm to binary...")

    # Initialize the MIPS assembler
    ks = keystone.Ks(keystone.KS_ARCH_MIPS, keystone.KS_MODE_MIPS32 + keystone.KS_MODE_LITTLE_ENDIAN)

    # Assemble the assembly code
    binary, count = ks.asm(mips_code)
    machine_code_bytes = struct.pack('B' * len(binary), *binary)

    # Print machine code bytes if verbose
    if (args.verbose):
        print("Machine code bytes:")
        print(machine_code_bytes)

    # Write machine code bytes to file if debug
    if (args.debug):
        print("Writing binary code to file...")
        with open("./out/mod.bin", "wb+") as file:
            file.write(machine_code_bytes)

    # 4 - Generate the mod.pnach file
    print("Generating mod.pnach file...")

    # Generate mod pnach code
    mod_pnach = pnach.Pnach(0x202E60B0, machine_code_bytes)

    # Print mod pnach code if verbose
    if (args.verbose):
        print("Mod pnach:")
        print(mod_pnach)

    # Generate pnach for function hook to jump to trampoline code
    """patch=1,EE,2013e380,extended,080B982C # j 0x2E60B0\n
    patch=1,EE,2013e384,extended,00000000 # nop\n"""
    hook_pnach = pnach.Pnach(0x2013e380, b"\x2C\x98\x0B\x08\x00\x00\x00\x00")
    
    # Print hook pnach code if verbose
    if (args.verbose):
        print("Hook pnach:")
        print(hook_pnach.lines)

    # Set up pnach header lines
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header_lines = "pnach file generated with sly-string-toolkit\n" \
    + "https://github.com/theonlyzac/sly-string-toolkit\n" \
    + f"date: {current_time}\n\n"

    # Write the final pnach file
    final_pnach = pnach.Pnach()
    final_pnach.merge_chunks(hook_pnach)
    final_pnach.merge_chunks(strings_pnach)
    final_pnach.merge_chunks(mod_pnach)
    final_pnach.set_header(header_lines)
    final_pnach.write_file(args.output)

    # Print final pnach if verbose
    if (args.verbose):
        print("Final pnach:")
        print(final_pnach)

    # 5 - Done!
    print(f"Wrote mod to {args.output}")

if __name__ == "__main__":
    main()
