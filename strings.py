import pnach, csv

def generate_strings_pnach(csv_file, start_address):
    # This function generates a pnach file with the strings from the csv file
    # and returns a tuple with the pnach lines and the arry of pointers to those strings

    # CSV rows are in the following format:
    # <string_id>,<string>,<optional_target_address>

    # 1 - Read the csv file and extract the strings
    string_pointers = []

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        # iterate over rows and add the string to the list, checking if the string has a target address
        # create an array of strings from the file
        strings = []
        manual_address_strings = []
        for row in reader:
            # if the length of the row is 3, add the address and string to the manual address strings array
            if len(row) == 3:
                manual_address_strings.append((int(row[0]), row[1].encode('utf-8') + b'\x00', int(row[2], 16)))
            # otherwise add the string to the strings array
            else:
                strings.append((int(row[0]), row[1].encode('utf-8') + b'\x00'))

    # 2 - Generate the pnach file

    # generate pnach for the strings that don't have a target address
    offset = start_address
    string_data = b''.join([string[1] for string in strings])
    pnach_lines = pnach.generate_pnach_lines(offset, string_data)

    # generate pnach for the strings that have a target address
    for string in manual_address_strings:
        pnach_lines += pnach.generate_pnach_lines(string[2], string[1])

    # 3 - Generate the pointers to the strings

    # generate pointers for the strings that don't have a target address
    for string in strings:
        string_pointers.append((string[0], offset))
        offset += len(string[1])

    # generate pointers for the strings that have a target address
    for string in manual_address_strings:
        string_pointers.append((string[0], string[2]))

    # 4 - Return the pnach lines and the array of pointers
    return (pnach_lines, string_pointers)

if __name__ == "__main__":
    string_pointers = generate_strings_pnach('strings.csv', 0x203C7980)
