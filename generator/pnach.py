"""
This file contains the Pnach class, which is used to generate pnach files.
"""

class Pnach:
    def __init__(self, address="", data=b""):
        self._header =""
        self._chunks = {}
        if data != b"":
            self.add_chunk(address, data)

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

    # Add a chunk of data to the pnach
    def add_chunk(self, address, data):
        self._chunks[address] = data

    # Get the chunks dictionary
    def get_chunks(self):
        return self._chunks

    # Merge another pnach object's chunks into this one
    def merge_chunks(self, other):
        self._chunks.update(other.get_chunks())

    # Generate pnach lines from address and data
    def gen_pnach_lines(self):
        pnach_lines = ""
        # Write each chunk of lines
        for address, data in self._chunks.items():
            for i in range(0, len(data), 4):
                pnach_code = address + i
                value = int.from_bytes(data[i:i + 4][::-1], 'big')
                line = f"patch=1,EE,{pnach_code:X},extended,{value:08X}\n"
                pnach_lines += line

        return pnach_lines

    # Write the pnach lines to a file with header
    def write_file(self, filename):
        with open(filename, "w+", encoding="iso-8859-1") as f:
            if self._header != "":
                f.write(self._header)
            f.write(self.lines)

    # Get a string of the pnach lines
    def __str__(self):
        return self.lines

    # Get a string representation of the object
    def __repr__(self):
        return f"Pnach object with {len(self._chunks)} chunks ({sum(len(chunk) for chunk in self._chunks.values())} bytes)"

if __name__ == "__main__":
    sample_bytes = b""
    with open("./out/mod.bin", "rb") as sample_file:
        sample_bytes = sample_file.read()
    sample_pnach = Pnach(0x202E60B0, bytes)
    print(sample_pnach)
