import strings, asm, pnach;
import os, sys;

if __name__ == "__main__":
    # Create the out folder if it doesn't exist
    if (not os.path.exists("./out")):
        os.mkdir("./out")

    # 1. Generate the strings.pnach file
    print("Generating strings.pnach file...")
    string_pointers = strings.generate_strings_pnach('strings.csv', 0x203C7980, "./out/07652DD9.strings.pnach")

    # 2. Generate the mod.s file
    print("Generating mod.s file...")
    asm.generate_asm(string_pointers, "./out/mod.s")

    # 3. Wait for user to assembly mod.o file and press any key
    input("Assemble mod.s into mod.o and press enter to continue...")
    
    # 4. Generate the mod.pnach file
    print("Generating mod.pnach file...")
    machine_code_bytes = pnach.read_bytes_from_file("./mod.o")
    pnach_lines = pnach.generate_pnach_lines(0x202E60B0, machine_code_bytes)
    # Hook the game function and jump to custom trampoline code
    pnach_lines += "# hook game function and jump to custom trampoline code\n"
    pnach_lines += "patch=1,EE,2013e380,extended,080B982C # j 0x2E60B0\n"
    pnach_lines += "patch=1,EE,2013e384,extended,00000000 # nop\n"
    # Write pnach to file
    pnach.write_pnach_file(pnach_lines, "./out/07652DD9.mod.pnach")

    # 5. Done!
    print("Done!")