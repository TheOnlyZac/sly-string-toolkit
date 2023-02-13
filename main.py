"""
Main file for Sly String Toolkit
"""
import os
import argparse
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from generator import Generator

DEBUG_FILE_OUTPUT = True

def main():
    """
    Main function, parses command line arguments and calls the pnach generator
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate PNACH file from CSV.')
    parser.add_argument('input_file', type=str, help='input CSV file name (default is strings.csv)', default="strings.csv")
    parser.add_argument('-o', '--output-dir', type=str, help='output directory (default is ./out/)', default="./out/")
    parser.add_argument('-r', '--region', type=str, help='the region of the game, support ntsc and pal (default is ntsc)', default="ntsc")
    parser.add_argument('-c', '--code-address', type=str, help='set the address where the pnach will inject the asm code')
    parser.add_argument('-s', '--strings-address', type=str, help='set the address where the pnach will inject the custom strings')
    parser.add_argument('-n', '--mod-name', type=str, help='name of the mod (default is same as input file)')
    parser.add_argument('-a', '--author', type=str, help='name of the author (default is Sly String Toolkit)', default="Sly String Toolkit")
    parser.add_argument('-d', '--dialect', type=str, help='the language of the strings file')
    parser.add_argument('-v', '--verbose', action='store_true', help='show verbose output')
    parser.add_argument('-l', '--live-edit', action='store_true', help='enable live editing of strings csv file')
    args = parser.parse_args()

    # Make sure the input file exists
    if (not os.path.exists(args.input_file)):
        print("Usage: python main.py [input_file] [-o output_dir] [-n mod_name]")
        return
    
    # Make sure input file is a complete path
    if (not os.path.isabs(args.input_file)):
        args.input_file = os.path.abspath(args.input_file)

    # Set verbose and debug flags on generator
    Generator.set_verbose(args.verbose)
    Generator.set_debug(DEBUG_FILE_OUTPUT)

    # Create the generator and generate the pnach
    generator = Generator(args.region, args.dialect, args.strings_address, args.code_address)

    # Check if live-edit flag is set
    if args.live_edit:
        print("Live editing enabled, make changes to the strings csv file and the pnach will be updated automatically.")
        # Create the observer and schedule the event handler
        observer = Observer()
        event_handler = FileSystemEventHandler()
        event_handler.on_modified = lambda event: generator.generate_pnach_file(args.input_file, args.output_dir, args.mod_name, args.author)
        observer.schedule(event_handler, path=os.path.dirname(args.input_file), recursive=False)
        
        # Start the observer and wait for keyboard interrupt
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        # Stop the observer
        observer.join()
    else:
        generator.generate_pnach_file(args.input_file, args.output_dir, args.mod_name, args.author)

if __name__ == "__main__":
    main()