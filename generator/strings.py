"""
Thie file contains the Strings class, which generates a pnach file with the strings from a csv
and returns a tuple with the pnach object and the array of pointers to the strings.
"""
import csv
from generator import pnach

class Strings:
    """
    This class reads a csv file and generates a pnach file with the strings
    and popoulates an array of pointers to the strings
    """
    def __init__(self, csv_file, start_address, csv_encoding='utf-8'):
        """
        Initializes the Strings object
        """
        self.csv_file = csv_file
        self.csv_encoding = csv_encoding
        self.start_address = start_address

    def gen_pnach_chunks(self):
        """
        Generates a pnach file with the strings from the csv file and returns
        a tuple with the pnach object and the array of pointers to the strings
        
        CSV rows are in the following format:
        <string_id>,<string>,<optional_target_address>
        """
        # 1 - Read the csv file and extract the strings
        id_string_pointer_pairs = []

        strings = []
        manual_address_strings = []
        with open(self.csv_file, 'r', encoding=self.csv_encoding) as file:
            reader = csv.reader(file)
            # iterate over rows and add the string to the list, checking if the string has a target address
            # create an array of strings from the file
            for row in reader:
                # if the length of the row is 3, add the address and string to the manual address strings array
                if len(row) > 2 and row[2] != '':
                    manual_address_strings.append((int(row[0]), row[1].encode('iso-8859-1') + b'\x00', int(row[2], 16)))
                # otherwise add the string to the strings array
                else:
                    try:
                        strings.append((int(row[0]), row[1].encode('iso-8859-1') + b'\x00'))
                    except UnicodeEncodeError as err:
                        print(f"Failed to encode string '{row[1]}'\nError: {err}")
                        strings.append((int(row[0]), "[error encoding string]".encode('iso-8859-1') + b'\x00'))

        # 2 - Generate the pnach file

        # gen pnach chunk for the strings that don't have a target address
        offset = self.start_address
        string_data = b''.join([string[1] for string in strings])
        auto_chunk = pnach.Chunk(offset, string_data)

        # gen pnach chunks for strings that have a target address
        manual_chunks = []
        for string in manual_address_strings:
            chunk = pnach.Chunk(string[2], string[1])
            manual_chunks.append(chunk)

        # 3 - Generate the pointers to the strings

        # generate pointers for the strings that don't have a target address
        for string in strings:
            id_string_pointer_pairs.append((string[0], offset))
            offset += len(string[1])

        # generate pointers for the strings that have a target address
        for string in manual_address_strings:
            id_string_pointer_pairs.append((string[0], string[2]))

        # set header for the pnach chunks
        auto_chunk.set_header(f"comment=Writing {len(id_string_pointer_pairs)} strings ({len(auto_chunk.get_bytes())} bytes) at {hex(self.start_address)}")
        for chunk in manual_chunks:
            chunk.set_header(f"comment=Writing 1 string ({len(chunk.get_bytes())} bytes) at {hex(self.start_address)}")
        
        # 4 - Return the pnach lines and the array of pointers
        return (auto_chunk, manual_chunks, id_string_pointer_pairs)

if __name__ == "__main__":
    sample_strings = Strings('strings.csv', 0x203C7980)
    sample_pnach = sample_strings.gen_pnach_chunks()
    print(sample_pnach.lines)
