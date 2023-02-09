import strings, asm, pnach;
import os, keystone, struct;

if __name__ == "__main__":
    # Create the out folder if it doesn't exist
    if (not os.path.exists("./out")):
        os.mkdir("./out")

    # 1 - Generate the strings pnach and populate string pointers
    print("Generating strings.pnach file...")
    pnach_lines, string_pointers = strings.generate_strings_pnach('strings.csv', 0x203C7980)

    # 2 - Generate the mod asm file
    print("Generating mod.s file...")
    mips_code = asm.generate_asm(string_pointers)

    with open("./out/mod.s", "w+") as f:
        f.write(mips_code);

    # 3 - Assemble the asm code to binary
    print("Assembling mod.s file to mod.o...")
    # Initialize the MIPS assembler
    ks = keystone.Ks(keystone.KS_ARCH_MIPS, keystone.KS_MODE_MIPS32 + keystone.KS_MODE_LITTLE_ENDIAN)
    # Assemble the assembly code
    binary, count = ks.asm(mips_code)

    with open("./out/mod.o", "wb+") as f:
        f.write(struct.pack('B' * len(binary), *binary))
    
    # 4 - Generate the mod.pnach file
    print("Generating mod.pnach file...")
    machine_code_bytes = pnach.read_bytes_from_file("./out/mod.o")

    # Generate mod pnach code
    pnach_lines += pnach.generate_pnach_lines(0x202E60B0, machine_code_bytes)

    # Hook the game function and jump to custom trampoline code
    pnach_lines += "patch=1,EE,2013e384,extended,00000000 # nop\n"
    pnach_lines += "# hook game function and jump to custom trampoline code\n"
    pnach_lines += "patch=1,EE,2013e380,extended,080B982C # j 0x2E60B0\n"
    
    # Write pnach to file
    pnach.write_pnach_file(pnach_lines, "./out/07652DD9.mod.pnach")

    # 5. Done!
    print("Done!")