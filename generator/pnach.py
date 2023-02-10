class Pnach:
    def __init__(self, address="", data=b"", filename="07652DD9.mod.pnach"):
        self._chunks = {}
        if data != b"":
            self.add_chunk(address, data)

    # Getter and setter for address
    def get_address(self):
        return self._address

    def set_address(self, address):
        self._address = address
        self.gen_pnach_lines(self._address, self._data)
    
    address = property(get_address, set_address)
    
    # Getter and setter for data
    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data
        self.gen_pnach_lines(self._address, self._data)
    
    data = property(get_data, set_data)
    
    # Getter for lines (no setter)
    def get_lines (self):
        return self.gen_pnach_lines()
    
    lines = property(get_lines)

    # String representation of the object
    def __str__(self):
        return f"patch=1,EE,{hex(self._address)},{hex(len(self._data))},{self._data}"

    # Generate pnach lines from address and data
    def gen_pnach_lines(self):
        pnach_lines = ""
        # Write each chunk of lines
        for address, data in self._chunks.items():
            for i in range(0, len(data), 4):
                line = f"patch=1,EE,{address + i:X},extended,{int.from_bytes(data[i:i + 4][::-1], 'big'):08X}\n"
                pnach_lines += line
        
        return pnach_lines
    
    def add_chunk(self, address, data):
        self._chunks[address] = data

    # Write the pnach lines to a file
    def write_file(self):
        with open(self.filename, "w+") as f:
            f.write(self.lines)

def read_bytes_from_file(filename):
    with open(filename, "rb") as f:
        return f.read()

if __name__ == "__main__":
    bytes = read_bytes_from_file("./out/mod.bin")
    pnach = Pnach(0x202E60B0, bytes)
    pnach.gen_pnach_lines()
