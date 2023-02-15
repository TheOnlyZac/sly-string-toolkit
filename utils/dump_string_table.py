"""
Script for extracting the string table from a ps2 memory dump to a csv file.
"""
import argparse

def dump_string_table(mem: bytes, string_table_start: int, mem_dump_start: int = 0x00000000):
    """
    Dumps the string table from a memory dump to a csv file.
    The original string table is an array list of id/string pointer pairs.
    """
    with open("strings.csv", "w+", encoding="iso-8859-1") as file:
        cur = string_table_start
        i = 0

        while True:
            i += 1

            string_id, string_pointer = int.from_bytes(mem[cur:cur+4], "little"), int.from_bytes(mem[cur+4:cur+8], "little")
            print(f"{string_id:X}, {string_pointer:X}")
            if (string_pointer == 0x000000) or (string_id > 0xFFFF) or (i > 1000):
                break
            string_pointer = string_pointer - mem_dump_start

            string = ""
            while True:
                byte = mem[string_pointer:string_pointer+1]
                if byte == b"\x00" or byte == b'':
                    break
                char = byte.decode("iso-8859-1")
                string += char
                string_pointer += 1

            # check if string contains quotation marks, commas, or newlines
            if "\"" in string or "," in string or "\n" in string:
                # if so, wrap the string in quotation marks
                string = f"\"{string}\""
            file.write(f"{string_id},{string}\n")
            cur += 8

if __name__ == "__main__":
    # get the command line arguments
    parser = argparse.ArgumentParser(description="Extracts the string table from a memory dump to a csv file.")
    parser.add_argument("mem-file", help="The PS2 memory dump file.")
    parser.add_argument("offset", help="The start offset of the string table in the mem dump.", type=lambda x: int(x, 16))
    parser.add_argument("-s", "--start", help="The start offset of the memory dump relative to the PS2 EE memory base.", type=lambda x: int(x, 16), default=0x00000000)
    args = parser.parse_args()

    # read the memory dump
    memory = None
    with open(args.mem_file, "rb") as mem_file:
        memory = mem_file.read()

    # dump the string table
    dump_string_table(memory, args.offset, args.start)
