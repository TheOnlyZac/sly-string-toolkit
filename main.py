from gen_strings import generate_strings_pnach
from gen_asm import generate_asm
from gen_pnach import generate_pnach, read_bytes_from_file
import os;

if __name__ == "__main__":
    # Create the out folder if it doesn't exist
    if (not os.path.exists("./out")):
        os.mkdir("./out")

    # 1. Generate the strings.pnach file
    print("Generating strings.pnach file...");
    string_pointers = generate_strings_pnach('strings.csv', 0x203C7980, "./out/07652DD9.strings.pnach")

    # 2. Generate the mod.s file
    print("Generating mod.s file...")
    generate_asm(string_pointers, "./out/mod.s")

    # 3. Wait for user to assembly mod.o file and press any key
    input("Assemble mod.s into mod.o and press enter to continue...")
    
    # 4. Generate the mod.pnach file
    print("Generating mod.pnach file...")
    bytes = read_bytes_from_file("./mod.o")
    generate_pnach(0x202E60B0, bytes, "out/07652DD9.mod.pnach")

    # 5. Done!
    print("Done!")