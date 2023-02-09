import pnach, csv

def generate_strings_pnach(csv_file, start_address, outfile="07652DD9.strings.pnach"):
    # This function generates a pnach file with the strings from the csv file
    # and returns the pointers to those strings

    # 1 - Read the csv file and extract the strings
    string_pointers = []

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        strings = [(int(row[0]), row[1].encode('utf-8') + b'\x00') for row in reader]

    # 2 - Generate the pnach file
    offset = start_address
    string_data = b''.join([string[1] for string in strings])
    pnach_lines = pnach.generate_pnach_lines(offset, string_data)
    pnach.write_pnach_file(pnach_lines, outfile)

    # 3 - Generate the pointers to the strings
    for string in strings:
        string_pointers.append((string[0], offset))
        offset += len(string[1])

    return string_pointers

"""def generate_pointers_pnach(string_pointers, start_address):
    pnach_file = ""
    for string_pointer in string_pointers:
        pnach_line = f"patch=1,EE,{start_address:X},extended,{string_pointer[1]:X}\n"
        pnach_file += pnach_line
        start_address += 4

    with open("pointers.pnach", "w+") as f:
        f.write(pnach_file)"""

if __name__ == "__main__":
    string_pointers = generate_strings_pnach('strings.csv', 0x203C7980)
    """generate_pointers_pnach(string_pointers, 0x202E6200)"""
