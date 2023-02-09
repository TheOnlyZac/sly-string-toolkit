# Sly String Toolkit

This is a toolkit for making string replacement mods for *Sly 2: Band of Thieves* for the PS2.

# Usage

1. Install Python 3.8 or higher.

2. Clone the repository with `git clone https://github.com/theonlyzac/sly-string-toolkit.git`

3. Install the dependencies with `pip install -r requirements.txt`

4. Place your `strings.csv` file with custom strings in the same folder as the script.

5. Run `python main.py` and follow the prompts.

6. Copy the `.pnach` files to your `pcsx2/cheats` folder and start the game.

## Assembling the .s file

While the script is running, it will produce an assembly code file `mod.s`, then pause and ask you to assemble it using a MIPS assembler.

Name the assembled file `mod.o` and put it in the same folder as the script, then press enter and it will continue generating the `.pnach` files.

## Output 

The script will output two files:

* `07652DD9.mod.pnach` - This is the main mod file. It contains the assembly code that hooks the string loader function.
* `07652DD9.strings.pnach` - This file contains the strings themselves.

You should copy both of these files to your `pcsx2/cheats` folder. You can change the name of the files if you want, but they must start with `07652DD9.` including the dot.

# Strings File Format

The strings file should be a CSV file. Each row should have the following format:

`<string id>,<string>`

where `<string id>` is the ID of the string you want to replace, and `<string>` is the string to replace it with.