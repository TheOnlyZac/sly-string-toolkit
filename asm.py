import csv

def generate_asm(id_string_pairs):
    #mips_code = "# hook game function and jump to custom trampoline code\n"
    #mips_code += "j 0x2E60B0\n"
    #mips_code += "nop\n\n"
    mips_code = "trampoline:\n"
    mips_code += "lw $v0, 0x4($a0)\n\n"
    mips_code += "# check if the ID matched is the string to replace\n"
    
    for string_id, string_ptr in id_string_pairs:
        mips_code += f"ori $t0, $zero, {string_id}\n"
        mips_code += f"bne $t0, $a1, done{string_id}\n"
        mips_code += "nop\n\n"
        mips_code += "# it matched, so replace the return string ptr with ptr to our custom string\n"
        mips_code += f"lui $v0, {hex(string_ptr >> 16)}\n"
        mips_code += f"ori $v0, $v0, {hex(string_ptr & 0xFFFF)}\n"
        mips_code += "nop\n\n"
        mips_code += f"done{string_id}:\n\n"
    
    mips_code += "# return from the original function\n"
    mips_code += "return:\n"
    mips_code += "jr $ra\n"
    mips_code += "nop\n"

    return mips_code

def generate_code_from_csv(filename):
    id_string_pairs = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader) # skip header row
        for row in reader:
            id_string_pairs.append((int(row[0], 16), int(row[1], 16)))
    
    mips_code = generate_asm(id_string_pairs)
    return mips_code

if __name__ == "__main__":
    generate_code_from_csv("string_ids_and_ptrs.csv")