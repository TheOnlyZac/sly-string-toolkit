"""
Driver for Sly String Toolkit.
"""
import os
import argparse
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from generator import Generator

DEBUG_ENABLED = False

def main():
    """
    Main function, parses command line arguments and calls the pnach generator
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Tool for generating PNACH from CSV to replace strings in Sly 2.')
    parser.add_argument('input_file', type=str, help='input CSV file name (default is strings.csv)', default="strings.csv")
    parser.add_argument('-o', '--output-dir', type=str, help='output directory (default is ./out/)', default="./out/")
    parser.add_argument('-r', '--region', type=str, help='the region of the game, support ntsc and pal (default is ntsc)', default="ntsc")
    parser.add_argument('-c', '--code-address', type=str, help='set the address where the pnach will inject the asm code')
    parser.add_argument('-s', '--strings-address', type=str, help='set the address where the pnach will inject the custom strings')
    parser.add_argument('-t', '--name', type=str, help='name of the mod (default is same as input file)')
    parser.add_argument('-a', '--author', type=str, help='name of the author (default is Sly String Toolkit)', default="Sly String Toolkit")
    parser.add_argument('-l', '--lang', type=str, help='language of the input CSV')
    parser.add_argument('-e', '--csv_encoding', type=str, help='the encoding of the input CSV file (default is utf-8)', default="utf-8")
    parser.add_argument('-v', '--verbose', action='store_true', help='show verbose output')
    parser.add_argument('--live-edit', action='store_true', help='enable live editing of strings csv file')
    args = parser.parse_args()

    # Make sure the input file exists
    if not os.path.exists(args.input_file):
        print(parser.format_help())
        print(f"Error: Input file {args.input_file} not found.")
        return

    # Make sure input file is a complete path
    if not os.path.isabs(args.input_file):
        args.input_file = os.path.abspath(args.input_file)

    # Set static flags on generator
    Generator.set_verbose(args.verbose)
    Generator.set_debug(DEBUG_ENABLED)

    # Create the generator and generate pnach
    generator = Generator(args.region, args.lang, args.strings_address, args.code_address)
    if args.live_edit:
        print("Live editing enabled. The pnach will be updated automatically when you save the csv file.")
        # Create the observer and schedule the event handler
        observer = Observer()
        event_handler = FileSystemEventHandler()
        event_handler.on_modified = lambda event: generator.generate_pnach_file(args.input_file, args.output_dir, args.name, args.author, args.csv_encoding)
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
        generator.generate_pnach_file(args.input_file, args.output_dir, args.name, args.author)

if __name__ == "__main__":
    main()
