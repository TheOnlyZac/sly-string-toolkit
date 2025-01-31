# Sly String Toolkit
<img src="thumb.png" alt="A screenshot of the Sly 2 title screen with strings replaced where game strings have been replaced with the name and link to the repository." align="right" style="float: right; margin: 10px; width: 300px">

This is a toolkit for making string replacement mods for *Sly 2: Band of Thieves* and *Sly 3: Honor Among Thieves* for the PS2. For a complete tutorial, see [this guide](https://slymods.info/wiki/Guide:Replacing_strings) on the SlyMods wiki.

# Usage

`python stringtoolkit.py [-g 2/3] [-r ntsc/pal] <options> input_file.csv`

These arguments are required:
* `-g <game>` - Which game the mod supports. `2` for Sly 2 or `3` for Sly 3 (required).
* `-r <region>` - Which region the mod supports. Can be `ntsc` or `pal` (required).

These arguments are optional:

* `-l <lang>` - The language the pnach should work for (PAL only). If not set, it will affect all languages.
* `-n <mod_name>` - The name of the mod. Shows in the PCSX2 GUI. The output file will be `<crc>.<mod_name>.pnach` (default is the same as the input file).
* `-a <author> ` The author of the mod. Shows in the PCSX2 GUI (default is "Sly String Toolkit").
* `-o <output_dir>` - The output directory for the pnach file (default is `./out/`).
  * Can be `en`, `fr`, `it`, `de`, `es`, `nd`, `pt`, `da`, `fi`, `no`, or `sv`.
  * Only one pnach can be used at a time, so if your mod supports multiple languages, you must post them as separate patches.
* `-c <asm_codecave>` - Change the address of the codecave where the mod's assembly code is injected.
* `-s <strings_codecave>` - Change the address of the codecave where the custom strings are injected.
* `--live-edit` - Enable live edit mode. This will allow you to edit the strings in the csv and the pnach will automatically update.
* `--verbose` - Enable verbose output.
* `--clps2c` - Output CLPS2C source code instead of raw pnach
* `-h` - Show help.

# Setup

1. Install Python 3.8 or higher.

2. Clone the repository with `git clone https://github.com/theonlyzac/sly-string-toolkit.git`

3. Create python environment with `python3 -m venv env`, then `source env/bin/activate` (Linux) or `.\env\Scripts\activate.bat` (Windows)

4. Install the dependencies with `pip install -r requirements.txt`

5. Use `stringtoolkit.py` as described in the section above to generate the `.pnach` file.

6. Put the `.pnach` file in your `PCSX2/cheats` folder, enable the cheat, and start the game.

# Output

The script will output one pnach file. It contains the assembly code to load the custom strings as well as the strings themselves.

You should put this file in your `pcsx2/cheats` folder. You can rename file if you want, but it must be in the format `<game_crc>.<mod_name>.pnach`.

# Strings CSV Format

The input file should be a CSV where each row has the following format:

`<string id>,<string>,<optional target address>`

* `<string id>` is the ID of the string you want to replace
* `<string>` is the string to replace it with
* `<optional target address>` is the address to write the string to. If not specified, it will be written with the rest of the strings in a block at the address specified by the `-a` option.

Everything after the third column is ignored by the script, so you can use it for notes if you want. You can make the file in Excel or Google Sheets and then export it as a CSV.

# Live Edit

The `--live-edit` option enables live edit mode. When enabled, the script will watch the input file for changes and update the pnach file automatically. This allows you to edit the strings in the CSV file while the game is running. Press `ctrl+c` to stop the script.

PCSX2 will not automatically reload the pnach file when it changes, so you will not see your changes immediately. You have to click "Reload cheats" in the game properties window, or reboot the game (and use a save state to quickly get back to where you were).

# How it works

This script hooks the string load function with custom code that instead loads the strings you specify in the CSV file. It does this by writing the strings to a block of memory and loads the strings from that block of memory instead of the original string table.

The way the game normally loads any string is by iterating over a table that contains the IDs for all the strings in the game. If it finds a match, it loads the string from the string table at the address specified by the string ID. This script hooks the string load function at the moment where it returns the pointer to the string.

Instead of returning the pointer to the original string, it runs our custom code which checks if there is a custom string with that ID. If so, it instead returns a pointer to the custom string. If not, it returns the pointer to the original string without any changes.

When you run the script, it first converts all the custom strings to hexadecimal values and generates a pnach which writes those strings to a specific block of unused RAM. It then generates and assembles the MIPS code which checks each custom string ID and returns the pointer to the custom string if it exists. Finally, it writes the assembly code to the pnach file and hooks the string load function.

# Credits

Special thanks to [zzamizz](https://github.com/zzamizz) for extensive testing and assistance with reverse engineering the string load functions.
