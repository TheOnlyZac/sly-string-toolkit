class Pnach:
    def __init__(self, address="", data=b""):
        self._header =""
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

    # Getter and setter for header
    def get_header(self):
        return self._header

    def set_header(self, header):
        self._header = header
    
    header = property(get_header, set_header)

    # Get a string of the pnach lines
    def __str__(self):
        return self.lines

    # Get a string representation of the object
    def __repr__(self):
        return f"Pnach object with {len(self._chunks)} chunks ({sum(len(chunk) for chunk in self._chunks.values())} bytes)"

    # Generate pnach lines from address and data
    def gen_pnach_lines(self):
        pnach_lines = ""
        # Write each chunk of lines
        for address, data in self._chunks.items():
            for i in range(0, len(data), 4):
                line = f"patch=1,EE,{address + i:X},extended,{int.from_bytes(data[i:i + 4][::-1], 'big'):08X}\n"
                pnach_lines += line
        
        return pnach_lines
    
    # Add a chunk of data to the pnach
    def add_chunk(self, address, data):
        self._chunks[address] = data

    # Merge another pnach object's chunks into this one
    def merge_chunks(self, other):
        self._chunks.update(other._chunks)

    # Write the pnach lines to a file with header
    def write_file(self, filename="07652DD9.mod.pnach"):
        with open(filename, "w+") as f:
            if self._header != "":
                f.write(self._header)
            f.write(self.lines)

if __name__ == "__main__":
    bytes = b""
    with open("./out/mod.bin", "rb") as f:
        bytes = f.read()
    pnach = Pnach(0x202E60B0, bytes)
    pnach.gen_pnach_lines()
    print(pnach.lines)
