# String Replacement Example

This directory contains example `.csv` files with replacement strings. The `.csv` files are used to generate `.pnach` files that PCSX2 can use to patch the game.

To generate the `.pnach` file, open a command prompt in the main directory and run `python main.py -i examples/<filename>.csv`. Then put the `.pnach` file in your `pcsx2/cheats` folder and start the game. You should see the new strings in-game.
* For a faster workflow, use the `-o` option to set your output directory to your `pcsx2/cheats` folder so you don't have to copy the file over every time you run the script.

You can use the `test.csv` file as a template for your own string replacement mods. If you upload the csv to Excel or Google Sheets for easier editing, make sure you save/export the sheet as a CSV file.
