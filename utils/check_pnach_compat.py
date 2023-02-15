"""
Script for checking if two pnach files are compatible with each other.
"""
import argparse
from typing import List

def get_addresses(pnach: str) -> List[int]:
    """
    Gets the memory addresses that are written to by a pnach file.
    """
    lines = pnach.split('\n')
    addresses = []

    for line in lines:
        if line.startswith("patch="):
            code_part_1 = line.split(",")[2]
            code_part_2 = line.split(",")[4]
            code_type = code_part_1[0]

            if code_type == "E":
                # 16-bit test conditional
                # E0nnvvvv taaaaaaa
                # Compares value at address @a to value @v, and executes next @n code llines only if the test condition @t is true
                address = int(code_part_2[1:8], 16)
                value = int(code_part_1[4:8], 16)
                num_lines = int(code_part_1[2:4], 16)
                condition = code_part_1[1]
            elif code_type == "2":
                # 32-bit constant write
                # 2aaaaaaa vvvvvvvv
                # Constantly writes a 32-bit value @v to the address @a.
                address = int(code_part_1[1:8], 16)
                value = int(code_part_2[0:8], 16)
                addresses.append(address)

    return addresses

def check_compatiblity(pnach_1: str, pnach_2: str):
    """
    Checks if two pnach files are compatible with each other. Two pnach files
    are compatible if they don't both write to the same memory addresses (unless
    the writes are qualified by conditional statements that are mutually exclusive).

    For the time being this script does not check for conditional statements and
    assumes that all writes are unconditional.
    """
    # get the memory addresses that are written to by each pnach file
    pnach_1_addresses = get_addresses(pnach_1)
    pnach_2_addresses = get_addresses(pnach_2)

    # check if any of the addresses are written to by both pnach files
    matches = []
    for address in pnach_1_addresses:
        if address in pnach_2_addresses:
            matches.append(address)

    if len(matches) > 0:
        matches_string = ", ".join([hex(match) for match in matches])
        return f"The following {len(matches)} addresses are written to by both pnach files: {matches_string}"
    else:
        return "The pnach files are compatible!"

def main():
    """
    Calls the check_compatiblity function with test pnach files.
    """
    # get the command line arguments
    parser = argparse.ArgumentParser(description="Checks if two pnach files are compatible with each other.")
    parser.add_argument("pnach_file_1", help="The first pnach file.")
    parser.add_argument("pnach_file_2", help="The second pnach file.")
    args = parser.parse_args()

    # read the pnach files
    pnach_1 = None
    print(args)
    with open(args.pnach_file_1, "r") as file:
        pnach_1 = file.read()
    pnach_2 = None
    with open(args.pnach_file_2, "r") as file:
        pnach_2 = file.read()

    result = check_compatiblity(pnach_1, pnach_2)
    print(result)

if __name__ == "__main__":
    main()
