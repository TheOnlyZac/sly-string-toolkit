import csv

class Trampoline:
    def __init__(self, id_string_pairs=[]):
        self.id_string_pairs = id_string_pairs

    def gen_asm(self):
        asm = "trampoline:\n"
        asm += "lw $v0, 0x4($a0)\n\n"
        
        for string_id, string_ptr in self.id_string_pairs:
            asm += f"# check matched string ID {string_id}\n"
            asm += f"ori $t0, $zero, {string_id}\n"
            asm += f"bne $t0, $a1, done{string_id}\n"
            asm += "nop\n\n"
            asm += f"lui $v0, {hex(string_ptr >> 16)}\n"
            asm += f"ori $v0, $v0, {hex(string_ptr & 0xFFFF)}\n"
            asm += "nop\n\n"
            asm += f"done{string_id}:\n\n"
        
        asm += "# return from the original function\n"
        asm += "return:\n"
        asm += "jr $ra\n"
        asm += "nop\n"

        return asm

    def gen_asm_from_csv(self, filename):
        self.id_string_pairs = []
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader) # skip header row
            for row in reader:
                self.id_string_pairs.append((int(row[0], 16), int(row[1], 16)))
        
        asm = self.gen_asm()
        return asm

if __name__ == "__main__":
    trampoline = Trampoline()
    trampoline.gen_asm_from_csv("strings.csv")
    