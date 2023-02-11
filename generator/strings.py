from generator import pnach
import csv

class Strings:
    def __init__(self, csv_file, start_address):
        self.csv_file = csv_file
        self.start_address = start_address

    def gen_pnach(self):
        """ Generates a pnach file with the strings from the csv file and returns 
        a tuple with the pnach object and the array of pointers to the strings

        CSV rows are in the following format:
        <string_id>,<string>,<optional_target_address>"""

        # 1 - Read the csv file and extract the strings
        id_string_pointer_pairs = []

        with open(self.csv_file, 'r', encoding='iso-8859-1') as file:
            reader = csv.reader(file)
            # iterate over rows and add the string to the list, checking if the string has a target address
            # create an array of strings from the file
            strings = []
            manual_address_strings = []
            for row in reader:
                print("\n\n\n\n")
                print(row)
                # if the length of the row is 3, add the address and string to the manual address strings array
                if len(row) == 3:
                    manual_address_strings.append((int(row[0]), row[1].encode('iso-8859-1') + b'\x00', int(row[2], 16)))
                # otherwise add the string to the strings array
                else:
                    strings.append((int(row[0]), row[1].encode('iso-8859-1') + b'\x00'))

        # 2 - Generate the pnach file
        pnach_obj = pnach.Pnach()

        # add pnach fhunks for the strings that don't have a target address
        offset = self.start_address
        string_data = b''.join([string[1] for string in strings])
        pnach_obj.add_chunk(offset, string_data)

        # add pnach chunks for strings that have a target address
        for string in manual_address_strings:
            pnach_obj.add_chunk(string[2], string[1])

        # 3 - Generate the pointers to the strings

        # generate pointers for the strings that don't have a target address
        for string in strings:
            id_string_pointer_pairs.append((string[0], offset))
            offset += len(string[1])

        # generate pointers for the strings that have a target address
        for string in manual_address_strings:
            id_string_pointer_pairs.append((string[0], string[2]))

        # 4 - Return the pnach lines and the array of pointers
        return (pnach_obj, id_string_pointer_pairs)

if __name__ == "__main__":
    strings = Strings('strings.csv', 0x203C7980)
    strings.gen_pnach()
    print(strings.lines)
