"""
Sly String Toolkit — Pnach Generator
A tool to generate pnach files from CSV files
"""
import os
import argparse
from datetime import datetime
import struct
import keystone
from generator import strings, trampoline, pnach

SLY2_NTSC_CRC = "07652DD9"
SLY2_NTSC_HOOK = 0x2013e380
SLY2_NTSC_ASM_DEFAULT = 0x202E60B0
SLY2_NTSC_STRINGS_DEFAULT = 0x203C7980

SLY2_PAL_CRC = "FDA1CBF6"
SLY2_PAL_HOOK = 0x2013e398
SLY2_PAL_ASM_DEFAULT = 0x202ED500
SLY2_PAL_STRINGS_DEFAULT = 0x203E99A0


def main():
    """Main function, parses command line arguments and generates the pnach file"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate PNACH file from CSV.')
    parser.add_argument('input_file', type=str, help='the input CSV file name (default is strings.csv)', default="strings.csv")
    parser.add_argument('-o', '--output', type=str, help='the output directory (default is ./out/)', default="./out/")
    parser.add_argument('-r', '--region', type=str, help='the region of the game, supports ntsc and pal (default is ntsc)', default="ntsc")
    parser.add_argument('-a', '--asm', type=str, help='set the address where the pnach will inject the asm code')
    parser.add_argument('-s', '--strings', type=str, help='set the address where the pnach will inject the custom strings')
    parser.add_argument('-n', '--name', type=str, help='name of the mod (default is same as input file')
    parser.add_argument('-v', '--verbose', action='store_true', help='show verbose output')
    parser.add_argument('-d', '--debug', action='store_true', help='output asm and bin files for debugging')
    args = parser.parse_args()

    # Set default CRC, hook, asm and strings addresses
    crc, hook_adr, asm_adr, strings_adr = (0x0, 0x0, 0x0, 0x0)
    if (args.region == "ntsc"):
        crc = SLY2_NTSC_CRC
        hook_adr = SLY2_NTSC_HOOK
        asm_adr = SLY2_NTSC_ASM_DEFAULT if args.asm is None else int(args.asm, 16)
        strings_adr = SLY2_NTSC_STRINGS_DEFAULT if args.strings is None else int(args.strings, 16)
    elif (args.region == "pal"):
        crc = SLY2_PAL_CRC
        hook_adr = SLY2_PAL_HOOK
        asm_adr = SLY2_PAL_ASM_DEFAULT if args.asm is None else int(args.asm, 16)
        strings_adr = SLY2_PAL_STRINGS_DEFAULT if args.strings is None else int(args.strings, 16)

    # Check if the input file was specified, and if not, if strings.csv exists
    if (args.input_file == "strings.csv" and not os.path.exists(args.input_file)):
        print("Usage: python main.py [input_file] [-o output_dir] [-n mod_name]")
        return

    # Create the out folder if it doesn't exist
    if (not os.path.exists("./out")):
        if (args.verbose):
            print("Creating out folder...")
        os.mkdir("./out")

    # 1 - Generate the strings pnach and populate string pointers
    print(f"Reading strings from {args.input_file} to 0x{strings_adr:X}...")
    strings_obj = strings.Strings(args.input_file, strings_adr)
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
        with open("./out/mod.asm", "w+", encoding="iso-8859-1") as file:
            file.write(mips_code)

    # 3 - Assemble the asm code to binary
    print(f"Assembling asm at 0x{asm_adr:X}...")

    # Initialize the MIPS assembler
    ks = keystone.Ks(keystone.KS_ARCH_MIPS, keystone.KS_MODE_MIPS32 + keystone.KS_MODE_LITTLE_ENDIAN)

    # Assemble the assembly code
    binary, count = ks.asm(mips_code)
    machine_code_bytes = struct.pack('B' * len(binary), *binary)

    # Print machine code bytes if verbose
    if (args.verbose):
        print(f"Assembled {count} bytes of machine code")
        print("Machine code bytes:")
        print(machine_code_bytes)

    # Write machine code bytes to file if debug
    if (args.debug):
        print("Writing binary code to file...")
        with open("./out/mod.bin", "wb+") as file:
            file.write(machine_code_bytes)

    # 4 - Generate the mod.pnach file
    print("Generating pnach file...")

    # Generate mod pnach code
    mod_pnach = pnach.Pnach(asm_adr, machine_code_bytes)

    # Print mod pnach code if verbose
    if (args.verbose):
        print("Mod pnach:")
        print(mod_pnach)

    # Generate pnach for function hook to jump to trampoline code
    hook_asm = f"j {asm_adr}\n"
    hook_binary, count = ks.asm(hook_asm)
    hook_bytes = struct.pack('B' * len(hook_binary), *hook_binary)

    # NTSC hook address: 0x2013e380
    # PAL hook address: 0x2013e398
    hook_pnach = pnach.Pnach(hook_adr, hook_bytes)

    # Print hook pnach code if verbose
    if (args.verbose):
        print("Hook pnach:")
        print(hook_pnach.lines)

    # Set up pnach header lines
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header_lines = "pnach file generated with sly-string-toolkit\n" \
        + "https://github.com/theonlyzac/sly-string-toolkit\n" \
        + f"date: {current_time}\n\n"

    # Set the mod name (default is same as input file)
    mod_name = args.name
    if (args.name is None):
        mod_name = os.path.splitext(os.path.basename(args.input_file))[0]

    # Write the final pnach file
    outfile = f"{args.output}\\{crc}.{mod_name}.pnach"
    final_pnach = pnach.Pnach()
    final_pnach.merge_chunks(hook_pnach)
    final_pnach.merge_chunks(mod_pnach)
    final_pnach.merge_chunks(strings_pnach)
    final_pnach.set_header(header_lines)
    final_pnach.write_file(outfile)

    # Print final pnach if verbose
    if (args.verbose):
        print("Final pnach:")
        print(final_pnach)

    # 5 - Done!
    print(f"Wrote pnach file to {outfile}")


if __name__ == "__main__":
    main()
