import strings, asm, pnach;
import os, argparse, keystone, struct;
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Generate PNACH file from CSV.')
    parser.add_argument('-i', '--input', type=str, help='input CSV file (default is strings.csv)', default="strings.csv")
    parser.add_argument('-o', '--output', type=str, help='output PNACH file (leave blank for default)', default="./out/07652DD9.mod.pnach")
    parser.add_argument('-v', '--verbose', action='store_true', help='show verbose output')
    
    args = parser.parse_args()
    
    # Create the out folder if it doesn't exist
    if (not os.path.exists("./out")):
        if (args.verbose):
            print("Creating out folder...")
        os.mkdir("./out")

    # 1 - Generate the strings pnach and populate string pointers
    print("Reading strings from csv...")

    string_pnach, string_pointers = strings.generate_strings_pnach(args.input, 0x203C7980)

    if (args.verbose):
        print("String pointers:")
        for string_id, string_ptr in string_pointers:
            print(f"ID: {hex(string_id)} | Ptr: {hex(string_ptr)}")

    # 2 - Generate the mod assembly code
    print("Generating assembly code...")

    mips_code = asm.generate_asm(string_pointers)
    
    if (args.verbose):
        print("Assembly code:")
        print(mips_code)

    # 3 - Assemble the asm code to binary
    print("Assembling asm to binary...")

    # Initialize the MIPS assembler
    ks = keystone.Ks(keystone.KS_ARCH_MIPS, keystone.KS_MODE_MIPS32 + keystone.KS_MODE_LITTLE_ENDIAN)

    # Assemble the assembly code
    binary, count = ks.asm(mips_code)
    machine_code_bytes = struct.pack('B' * len(binary), *binary)

    if (args.verbose):
        print("Machine code bytes:")
        print(machine_code_bytes)

    # 4 - Generate the mod.pnach file
    print("Generating mod.pnach file...")

    # Generate mod pnach code
    mod_pnach = pnach.generate_pnach_lines(0x202E60B0, machine_code_bytes)
    if (args.verbose):
        print("Mod pnach code:")
        print(mod_pnach)

    # Add function hook for jump to custom trampoline code
    hook_pnach = "patch=1,EE,2013e384,extended,00000000 # nop\n"
    hook_pnach += "patch=1,EE,2013e380,extended,080B982C # j 0x2E60B0\n"
    
    # Add header to pnach file
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header_pnach = "pnach file generated with sly-string-toolkit\n"
    header_pnach += "https://github.com/theonlyzac/sly-string-toolkit\n"
    header_pnach += f"date: {current_time}\n\n"

    # Write the final pnach file
    final_pnach = header_pnach + string_pnach + mod_pnach + hook_pnach
    pnach.write_pnach_file(final_pnach, f"{args.output}")

    # 5 - Done!
    print(f"Wrote mod to {args.output}")

if __name__ == "__main__":
    main()