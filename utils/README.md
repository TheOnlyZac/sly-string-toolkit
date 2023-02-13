# Utilities

This folder contains some helpful utilities for working with strings and pnach files.

## dump_string_table.py

`python dump_string_table.py <path to ps2 memory dump> <offset to string table>`

This script will dump the string table from a ps2 memory dump. It will output a file called `strings.csv` in the this directory. This is useful for finding the ID of a string you want to replace.

If your memory dump doesn't start from the PCSX2 elf base (usually 0x20000000), use the `-s` or `--start` option to set the start offset of your memory dump. For example, if your memory dump is of the region from 0x20100000 to 0x20FFFFFF, use `-s 100000`.

### Example

There is a sample `mem.bin` file in this directory that you can use to test this script. It is small segment of memory from Cairo in the PAL version. The string table starts at offset `0x10`, and the memdump begins at 0x204BA440, so run the script with `python dump_string_table.py mem.bin 10 -s 4BA440`.

## check_pnach_compat.py

`python check_pnach_compat.py <path to first pnach> <path to second pnach>`

This script will check if two pnach files are compatible with each other. When run, it will ouput a list of all the addresses that are in both pnach files. If the pnach files are compatible, this list should be empty and it will tell you as much.

Two pnach files are compatible if they don't both write to the same memory addresses (unless the writes are qualified by conditional statements that are mutually exclusive). In its current state, the script does not check for conditional statements and assumes that all writes are unconditional.
