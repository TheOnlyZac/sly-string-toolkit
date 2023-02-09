import strings, asm, pnach;
import os, keystone, struct, argparse;
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Generate PNACH file from CSV.')
    parser.add_argument('-i', '--input', type=str, help='input CSV file (default is strings.csv)', default="strings.csv")
    parser.add_argument('-o', '--output', type=str, help='output PNACH file (leave blank for default)', default="./out/07652DD9.mod.pnach")
    args = parser.parse_args()
    
    # Create the out folder if it doesn't exist
    if (not os.path.exists("./out")):
        os.mkdir("./out")

    # 1 - Generate the strings pnach and populate string pointers
    print("Generating strings.pnach file...")
    string_pnach, string_pointers = strings.generate_strings_pnach(args.input, 0x203C7980)

    # 2 - Generate the mod asm file
    print("Generating mod.s file...")
    mips_code = asm.generate_asm(string_pointers)

    # 3 - Assemble the asm code to binary
    print("Assembling mod.s file to mod.o...")
    # Initialize the MIPS assembler
    ks = keystone.Ks(keystone.KS_ARCH_MIPS, keystone.KS_MODE_MIPS32 + keystone.KS_MODE_LITTLE_ENDIAN)
    # Assemble the assembly code
    binary, count = ks.asm(mips_code)

    # 4 - Generate the mod.pnach file
    print("Generating mod.pnach file...")
    machine_code_bytes = struct.pack('B' * len(binary), *binary)

    # Generate mod pnach code
    mod_pnach = pnach.generate_pnach_lines(0x202E60B0, machine_code_bytes)

    # Hook the game function and jump to custom trampoline code
    hook_pnach = "patch=1,EE,2013e384,extended,00000000 # nop\n"
    hook_pnach += "patch=1,EE,2013e380,extended,080B982C # j 0x2E60B0\n"
    
    # Write pnach to file
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header_pnach = "pnach file generated with sly-string-toolkit\n"
    header_pnach += "https://github.com/theonlyzac/sly-string-toolkit\n"
    header_pnach += f"date: {current_time}\n\n"

    final_pnach = header_pnach + string_pnach + mod_pnach + hook_pnach
    pnach.write_pnach_file(final_pnach, f"{args.output}")

    # 5. Done!
    print("Done!")

if __name__ == "__main__":
    main()