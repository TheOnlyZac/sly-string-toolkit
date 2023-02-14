"""
This file contains the Pnach and Chunk classes which are used to generate pnach files.
"""

class Chunk:
    """
    Chunk class, used to generate chunks of code lines for pnach files.
    """
    def __init__(self, address, data=b"", header=""):
        """
        Constructor for the Chunk class.
        """
        self._address = address
        self._bytes = data
        self._header = header
    
    # Getter and setter for address
    def get_address(self):
        """
        Returns the address of the chunk.
        """
        return self._address
    
    def set_address(self, address):
        """
        Sets the address of the chunk.
        """
        self._address = address
    
    # Getter and setter for bytes
    def get_bytes(self):
        """
        Returns the bytes of the chunk.
        """
        return self._bytes

    def set_bytes(self, bytes):
        """
        Sets the bytes of the chunk.
        """
        self._bytes = bytes
    
    # Getter and setter for header
    def get_header(self):
        """
        Returns the header of the chunk.
        """
        return self._header
    
    def set_header(self, header):
        """
        Sets the header of the chunk.
        """
        self._header = header

    # Getter for size
    def get_size(self):
        """
        Returns the size of the chunk in bytes.
        """
        return len(self._bytes)
    
    size = property(get_size)

    # Get code lines as array
    def get_code_lines(self):
        """
        Returns the code lines of the chunk as an array.
        """
        code_lines = []
        for i in range(0, self.size, 4):
            address = self._address + i
            bytes = self._bytes[i:i+4]
            # reverse byte order
            bytes = bytes[::-1]

            value = int.from_bytes(bytes, 'big')
            line = f"patch=1,EE,{address:X},extended,{value:08X}"
            code_lines.append(line)
        return code_lines
    
    def __str__(self):
        """
        Returns a string with the chunk's header + code lines.
        """
        chunk_str = ""
        if self._header != "":
            chunk_str += self._header + '\n'
        chunk_str += '\n'.join(self.get_code_lines())
        return chunk_str
    
    def __repr__(self):
        """
        Returns a string representation of the chunk.
        """
        return f"Chunk: {self._bytes} bytes at address {self._address:X}"
        

class Pnach:
    """
    Pnach class, used to generate pnach files.
    """
    def __init__(self, address="", data=b"", header=""):
        """
        Constructor for the Pnach class.
        """
        self._chunks = []
        self._conditionals = {}
        self._header = header
        if data != b"":
            self.create_chunk(address, data, header)

    # Getter for array of lines (no setter)
    def get_code_lines(self):
        """
        Returns an array of lines for the pnach file.
        """
        code_lines = []
        # Write each chunk of lines
        for chunk in self._chunks:
            code_lines += chunk.get_code_lines()
        
        return code_lines

    code_lines = property(get_code_lines)

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

    # Get and add conditionals
    def get_conditionals(self):
        """
        Returns the conditional for the pnach file.
        """
        return self._conditionals
    
    def add_conditional(self, address, value, type="eq"):
        """
        Sets the conditional for the pnach file. The pnach will
        only be applied if the given address has the given value.
        """
        # Switch the type to the correct value
        if type == "eq":
            type = 0
        elif type == "neq":
            type = 1
        
        # Add the conditional
        self._conditionals.update({ "address": address, "value": value, "type": type })

    # Chunk methods
    def create_chunk(self, address, data, header=""):
        """
        Adds a chunk of data to the pnach starting at the given address.
        """
        new_chunk = Chunk(address, data, header)
        self._chunks.append(new_chunk)

    def add_chunk(self, chunk):
        """
        Adds a chunk to the pnach.
        """
        self._chunks.append(chunk)

    def get_chunks(self):
        """
        Returns the array of chunks.
        """
        return self._chunks

    def merge_chunks(self, other):
        """
        Merges another pnach object's chunks into this one.
        """
        self._chunks += other.get_chunks()

    def get_chunk_bytes(self):
        """
        Returns all the bytes from each chunk.
        """
        chunk_bytes = b""
        for chunk in self._chunks:
            chunk_bytes += chunk.get_bytes()
        return chunk_bytes

    # Write pnach to file
    def write_file(self, filename):
        """
        Writes the pnach lines to a file with header.
        """
        with open(filename, "w+", encoding="utf-8") as f:
            if self._header != "":
                f.write(self._header)
            for chunk in self._chunks:
                f.write(str(chunk))
                f.write("\n")

    # String from pnach lines
    def __str__(self):
        """
        Returns a string with the pnach lines.
        """
        pnach_str = ""

        # Write header
        if self._header != "":
            pnach_str += self._header + "\n"

        # If there are no conditionals, write all lines
        if len(self._conditionals) == 0:
            # Write all pnach code lines
            pnach_str += '\n'.join([str(chunk) for chunk in self._chunks]) + "\n"
            return pnach_str

        # If there are conditionals, write conditional lines
        # Conditionals can only check 0xFF lines at a time,
        # so we need to split up chunks into groups of 0xFF lines
    
        # Get conditional values
        cond_address = self._conditionals['address']
        cond_value = self._conditionals['value']
        cond_type = self._conditionals['type']
        cond_operator = "==" if cond_type == 0 else "!="
        for chunk in self._chunks:
            # Add chunk header
            if chunk.get_header() != "":
                pnach_str += chunk.get_header() + "\n"

            # Get chunk lines
            lines = chunk.get_code_lines()
            num_lines = len(lines)

            # Write lines in groups of 0xFF
            for i in range(0, num_lines, 0xFF):
                # 16-bit conditional if-equal pnach line:
                # patch=1,EE,E0nnvvvv,extended,taaaaaaa
                # Compares value at address @a to value @v, and executes next @n code llines only if condition @t is met.
                num_lines_remaining = num_lines - i
                num_lines_to_write = 0xFF if num_lines_remaining > 0xFF else num_lines_remaining
                # Add conditional line
                pnach_str += f"-- Conditional: if *{cond_address:X} {cond_operator} 0x{cond_value:X} do {num_lines_to_write} lines\n"
                pnach_str += f"patch=1,EE,E0{num_lines_to_write:02X}{cond_value:04X},extended,{cond_type:1X}{cond_address:07X}\n"
                # Write lines to pnach
                pnach_str += '\n'.join(lines[i:i + num_lines_to_write]) + "\n"
        
        return pnach_str

    # String representation of pnach object
    def __repr__(self):
        """
        Returns a string representation of the pnach object.
        """
        return f"Pnach: {len(self._chunks)} chunks ({sum(len(chunk) for chunk in self._chunks)} bytes)"

if __name__ == "__main__":
    sample_bytes = b""
    with open("./out/mod.bin", "rb") as sample_file:
        sample_bytes = sample_file.read()
    sample_pnach = Pnach(0x202E60B0, bytes)
    print(sample_pnach)
