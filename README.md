# Sly String Toolkit

This is a toolkit for making string replacement mods for *Sly 2: Band of Thieves* for the PS2.

# Usage

`python main.py <options>`

The script supports the following optional arguments:

* `-i <inputfile>` - The name of the input csv file (default is `./strings.csv`)
* `-o <outputfile>` - The name of the output pnach file (default is `out/07652DD9.mod.pnach`)
* `-a <address>` - The address to write the strings to (default is `203C7980`)
* `-d` - Output `out.asm` and `out.bin` files for debugging
* `-v` - Enable verbose output
* `-h` - Show help

# Getting started 

1. Install Python 3.8 or higher.

2. Clone the repository with `git clone https://github.com/theonlyzac/sly-string-toolkit.git`

3. Install the dependencies with `pip install -r requirements.txt`

4. Run `python main.py` to generate the `.pnach` files.
   * Use the `-i` and `-o` arguments to specify the input and output files.

6. Put the `.pnach` file in your `pcsx2/cheats` folder and start the game.

## Output 

The script will output one pnach file. It contains the assembly code to load the custom strings and the strings themselves.

You should put this file in your `pcsx2/cheats` folder. You can change the name of the file if you want, but it must start with `07652DD9.` including the dot.

# Strings File Format

The input file should be a CSV where each row has the following format:

`<string id>,<string>,<optional target address>`

* `<string id>` is the ID of the string you want to replace
* `<string>` is the string to replace it with
* `<optional target address>` is the address to write the string to. If not specified, it will be written with the rest of the strings in a block at the address specified by the `-a` option.

Everything after the third column is ignored by the script, so you can use them for notes if you want. You can make the file in Excel or Google Sheets and then export it as a CSV.
