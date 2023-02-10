# String Replacement Example

This directory contains a file called `strings.csv`. It contains two strings that replace the text on the title screen, "Press START button for New Game" and "Press SELECT button for Menu".

To generate the `.pnach` file, open a command prompt in the main directory and run `python main.py -i exmaple/string.csv`. Then put the `.pnach` file in your `pcsx2/cheats` folder and start the game. You should see the new text on the title screen.
* For a faster workflow, use the `-o` option to set your output directory to your `pcsx2/cheats` folder so you don't have to copy the file over every time you run the script.

You can use this csv file as a template for your own string replacement mods. If you upload the csv to Excel or Google Sheets for easier editing, just make sure you save/export the sheet as a `.csv` file.
