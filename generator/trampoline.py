"""
This file contains the Trampoline class, which generates the trampoline assembly code
for accessing the custom string table.
"""
import csv

class Trampoline:
    """
    Trampoline class
    """
    def __init__(self, id_string_pairs: list = None):
        """
        Initializes the trampoline with the specified ID/string pairs
        """
        if id_string_pairs is None:
            self.id_string_pairs = []
        else:
            self.id_string_pairs = id_string_pairs

    def gen_asm(self, hook_delayslot) -> str:
        """
        Generates the trampoline assembly code from the ID/string pairs on the object
        """
        asm = "trampoline:\n"
        asm += f"{hook_delayslot}\n"

        for string_id, string_ptr in self.id_string_pairs:
            asm += f"# check matched string ID {string_id}\n"
            asm += f"ori $t0, $zero, {string_id}\n"
            asm += f"bne $t0, $a1, done{string_id}\n"
            #asm += "nop\n"
            asm += f"lui $v0, {hex(string_ptr >> 16)}\n"
            asm += f"ori $v0, $v0, {hex(string_ptr & 0xFFFF)}\n"
            #asm += "nop\n"
            asm += f"done{string_id}:\n"

        asm += "# return from the original function\n"
        asm += "return:\n"
        asm += "jr $ra\n"
        asm += "nop\n"

        return asm

    def gen_asm_from_csv(self, filename: str) -> str:
        """
        Read the ID/string pairs from a csv and generates the assembly code
        """
        self.id_string_pairs = []
        with open(filename, 'r', encoding='iso') as csvfile:
            reader = csv.reader(csvfile)
            next(reader) # skip header row
            for row in reader:
                self.id_string_pairs.append((int(row[0], 16), int(row[1], 16)))

        asm = self.gen_asm()
        return asm

def main():
    """
    Main function for testing
    """
    trampoline = Trampoline()
    trampoline.gen_asm_from_csv("strings.csv")
    print(trampoline.gen_asm())

if __name__ == "__main__":
    main()
