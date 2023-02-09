def write_pnach(address, byte_string):
    pnach_file = ""
    for i in range(0, len(byte_string), 4):
        # reverse the byte order


        pnach_line = f"patch=1,EE,{address + i:X},extended,{int.from_bytes(byte_string[i:i + 4][::-1], 'big'):08X}\n"
        pnach_file += pnach_line
    return pnach_file

def generate_pnach(address, byte_string, filename="07652DD9.mod.pnach"):
    pnach = write_pnach(address, byte_string)
    with open(filename, "w+") as f:
        f.write(pnach)

def read_bytes_from_file(filename):
    with open(filename, "rb") as f:
        return f.read()

if __name__ == "__main__":
    bytes = read_bytes_from_file("mod.o")
    generate_pnach(0x202E60B0, bytes)
