def generate_pnach_lines(address, byte_string):
    pnach_lines = ""
    for i in range(0, len(byte_string), 4):
        line = f"patch=1,EE,{address + i:X},extended,{int.from_bytes(byte_string[i:i + 4][::-1], 'big'):08X}\n"
        pnach_lines += line
    
    return pnach_lines

def write_pnach_file(pnach_lines, filename="07652DD9.mod.pnach"):
    with open(filename, "w+") as f:
        f.write(pnach_lines)

def read_bytes_from_file(filename):
    with open(filename, "rb") as f:
        return f.read()

if __name__ == "__main__":
    bytes = read_bytes_from_file("mod.o")
    generate_pnach_lines(0x202E60B0, bytes)
