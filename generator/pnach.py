"""
This file contains the Pnach class, which is used to generate pnach files.
"""

class Pnach:
    """
    Pnach class, used to generate pnach files.
    """
    def __init__(self, address="", data=b""):
        """
        Constructor for the Pnach class.
        """
        self._header =""
        self._chunks = {}
        if data != b"":
            self.add_chunk(address, data)

    # Getter for array of lines (no setter)
    def get_lines(self):
        """
        Returns an array of lines for the pnach file.
        """
        lines = []
        # Write each chunk of lines
        for address, data in self._chunks.items():
            for i in range(0, len(data), 4):
                pnach_code = address + i
                value = int.from_bytes(data[i:i + 4][::-1], 'big')
                line = f"patch=1,EE,{pnach_code:X},extended,{value:08X}"
                lines.append(line)
        
        return lines

    lines = property(get_lines)

    # Getter and setter for header
    def get_header(self):
        """
        Returns the header for the pnach file.
        """
        return self._header

    def set_header(self, header):
        """
        Sets the header for the pnach file.
        """
        self._header = header

    header = property(get_header, set_header)

    # Chunk methods
    def add_chunk(self, address, data):
        """
        Adds a chunk of data to the pnach starting at the given address.
        """
        self._chunks[address] = data

    def get_chunks(self):
        """
        Returns the dictionary of chunks.
        """
        return self._chunks

    def get_bytes(self):
        """
        Returns all the bytes from each chunk.
        """
        return b"".join(self._chunks.values())

    def merge_chunks(self, other):
        """
        Merges another pnach object's chunks into this one.
        """
        self._chunks.update(other.get_chunks())

    # Write pnach to file
    def write_file(self, filename):
        """
        Writes the pnach lines to a file with header.
        """
        with open(filename, "w+", encoding="iso-8859-1") as f:
            if self._header != "":
                f.write(self._header)
            f.write(self.lines)

    # String from pnach lines
    def __str__(self):
        """
        Returns a string with the pnach lines.
        """
        pnach_str = ""

        # Write header
        if self._header != "":
            pnach_str += self._header + "\n"

        # Write pnach code lines
        pnach_str += '\n'.join(self.lines) + "\n"

        return pnach_str

    # String representation of pnach object
    def __repr__(self):
        """
        Returns a string representation of the pnach object.
        """
        return f"Pnach object with {len(self._chunks)} chunks ({sum(len(chunk) for chunk in self._chunks.values())} bytes)"

if __name__ == "__main__":
    sample_bytes = b""
    with open("./out/mod.bin", "rb") as sample_file:
        sample_bytes = sample_file.read()
    sample_pnach = Pnach(0x202E60B0, bytes)
    print(sample_pnach)
