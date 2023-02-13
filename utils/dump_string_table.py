"""
Extracts the string table from a memory dump to a csv file.
"""
import argparse

def dump_string_table(mem, string_table_start, mem_dump_start=0x00000000):
    """
    Dumps the string IDs and strings to a csv file.
    The string table is an array list of id/string pointer pairs.
    """

    with open("strings.csv", "w+", encoding="utf-8") as file:
        cur = string_table_start
        i = 0

        while True:
            i += 1

            id, pointer = int.from_bytes(mem[cur:cur+4], "little"), int.from_bytes(mem[cur+4:cur+8], "little")
            print(f"{id:X}, {pointer:X}")
            if (pointer == 0x000000) or (id > 0xFFFF) or (i > 1000):
                break
            pointer = pointer - mem_dump_start
            
            string = ""
            while True:
                byte = mem[pointer:pointer+1]
                if byte == b"\x00" or byte == b'':
                    break
                char = byte.decode("iso-8859-1")
                string += char
                pointer += 1

            # check if string contains quotation marks, commas, or newlines
            if "\"" in string or "," in string or "\n" in string:
                # if so, wrap the string in quotation marks
                string = f"\"{string}\""
            file.write(f"{id},{string}\n")
            cur += 8        

if __name__ == "__main__":
    # get the command line arguments
    parser = argparse.ArgumentParser(description="Extracts the string table from a memory dump to a csv file.")
    parser.add_argument("mem_file", help="The memory dump file.")
    parser.add_argument("offset", help="The start of the string table.", type=lambda x: int(x, 16))
    parser.add_argument("-s", "--start", help="The start of the memory dump.", type=lambda x: int(x, 16), default=0x00000000)
    args = parser.parse_args()

    # read the memory dump
    memory = None
    with open(args.mem_file, "rb") as file:
        memory = file.read()

    # dump the string table
    dump_string_table(memory, args.offset, args.start)