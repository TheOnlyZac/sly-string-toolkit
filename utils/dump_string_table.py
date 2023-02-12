"""Extracts the string table from a memory dump to a csv file."""

STRING_TABLE_START = 0x10

def dump_string_table(mem, string_table_start):
    """Dumps the string IDs and strings to a csv file.
    The string table is an array list of id/string pointer pairs.
    The strings are null terminated and the end of the array will be marked by a null pointer."""

    with open("string_table.csv", "w+", encoding="iso-8859-1") as file:
        file.write("id,string\n")
        
        cur = string_table_start
        i = 0

        while True:
            i += 1

            id, pointer = int.from_bytes(mem[cur:cur+4], "little"), int.from_bytes(mem[cur+4:cur+8], "little")
            print(f"{id:X}, {pointer:X}")
            if pointer == 0x000000 or i > 500:
                break
            pointer = pointer - 0x4BA440
            
            string = ""
            while True:
                # subtract 0x4BA440 from the pointer to get the offset in the file

                char = mem[pointer:pointer+1]
                if char == b"\x00" or char == b'':
                    break
                string += char.decode("iso-8859-1")
                pointer += 1

            # check if string contains quotation marks, commas, or newlines
            if "\"" in string or "," in string or "\n" in string:
                # if so, wrap the string in quotation marks
                string = f"\"{string}\""
            file.write(f"{id},{string}\n")
            cur += 8
        
def main():
    mem = None
    with open("mem.bin", "rb") as file:
        mem = file.read()

    dump_string_table(mem, STRING_TABLE_START)
        

if __name__ == "__main__":
    main()