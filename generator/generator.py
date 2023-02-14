"""
This file contains the generator class, which generates a pnach file from a CSV file
"""
import os
from datetime import datetime
import struct
import keystone
from generator import strings, trampoline, pnach
from utils import Assembler

SLY2_NTSC_CRC = "07652DD9"
SLY2_NTSC_HOOK = 0x2013e380
SLY2_NTSC_ASM_DEFAULT = 0x202E60B0
SLY2_NTSC_STRINGS_DEFAULT = 0x203C7980

SLY2_PAL_CRC = "FDA1CBF6"
SLY2_PAL_HOOK = 0x2013e398
SLY2_PAL_ASM_DEFAULT = 0x202ED500
SLY2_PAL_STRINGS_DEFAULT = 0x203CF190

LANGUAGE_IDS = {
    "en": 0, # english
    "fr": 1, # french
    "it": 2, # italian
    "de": 3, # german
    "es": 4, # spanish
    "nd": 5, # dutch
    "pt": 6, # portuguese
    "da": 7, # danish
    "fi": 8, # finnish
    "no": 9, # norwegian
    "sv": 10, # swedish
}

class Generator:
    """
    Generator class, generates a pnach file from a CSV file
    """
    # Init variables
    verbose = False
    debug = False

    def __init__(self, region="ntsc", lang=None, strings_address=None, code_address=None):
        """
        Initializes the generator with the specified region and addresses
        """
        # Set region
        self.region = region.lower()

        # Set code + strings addresses and lang based on region
        if (region == "ntsc"):
            self.strings_adr = SLY2_NTSC_STRINGS_DEFAULT if strings_address is None else strings_address
            self.code_address = SLY2_NTSC_ASM_DEFAULT if code_address is None else code_address
            
            if (lang is not None):
                print("Warning: Language selection is not supported for NTSC region, using English")
                self.lang = LANGUAGE_IDS["en"]
            else:
                self.lang = None
        elif (region == "pal"):
            self.strings_adr = SLY2_PAL_STRINGS_DEFAULT if strings_address is None else strings_address
            self.code_address = SLY2_PAL_ASM_DEFAULT if code_address is None else code_address
            self.lang = LANGUAGE_IDS[lang.lower()] if lang is not None else None
        else:
            raise Exception(f"Error: Region {region} not supported, must be `ntsc` or `pal`")

        # Set hook address based on region
        self.hook_adr = SLY2_NTSC_HOOK if self.region == "ntsc" else SLY2_PAL_HOOK

        # Ensure addresses are ints
        if (type(self.strings_adr) == str):
            self.strings_adr = int(self.strings_adr, 16)
        if (type(self.code_address) == str):
            self.code_address = int(self.code_address, 16)
        if (type(self.hook_adr) == str):
            self.hook_adr = int(self.hook_adr, 16)


    @staticmethod
    def set_verbose(verbose):
        """
        Sets the verbose flag
        """
        Generator.verbose = verbose
        if (verbose):
            print("Verbose output enabled")

    @staticmethod
    def set_debug(debug):
        """
        Sets the debug flag
        """
        Generator.debug = debug
        if (debug):
            print("Debug output enabled")

    @staticmethod
    def assemble(asm_code):
        """
        Assembles the given assembly code to binary and converts it to a byte array
        """
        # Assemble the assembly code
        assembler = Assembler(keystone.KS_ARCH_MIPS, keystone.KS_MODE_MIPS32 + keystone.KS_MODE_LITTLE_ENDIAN)
        binary, count = assembler.assemble(asm_code)

        # Convert the binary to bytes
        machine_code_bytes = struct.pack('B' * len(binary), *binary)

        # Print machine code bytes if verbose
        if (Generator.verbose):
            print(f"Assembled {count} bytes of machine code")
            print("Machine code bytes:")
            print(binary)

        # Write machine code bytes to file if debug
        if (Generator.debug):
            print("Writing binary code to file...")
            with open("./out/mod.bin", "wb+") as file:
                file.write(machine_code_bytes)

        return machine_code_bytes, count

    def _gen_strings_from_csv(self, csv_file):
        """
        Generates the strings pnach and populate string pointers
        """
        if (self.verbose):
            print(f"Reading strings from {csv_file} to 0x{self.strings_adr:X}...")

        # Ensure file exists
        if (not os.path.isfile(csv_file)):
            raise Exception(f"Error: File {csv_file} does not exist")

        strings_obj = strings.Strings(csv_file, self.strings_adr)
        auto_strings_chunk, manual_string_chunks, string_pointers = strings_obj.gen_pnach_chunks()

        # Print string pointers if verbose
        if (self.verbose):
            print("String pointers:")
            for string_id, string_ptr in string_pointers:
                print(f"ID: {hex(string_id)} | Ptr: {hex(string_ptr)}")
            print("Auto strings pnach:")
            print(auto_strings_chunk)
            print("Manual strings pnach:")
            print([str(chunk) for chunk in manual_string_chunks].join("\n"))

        return auto_strings_chunk, manual_string_chunks, string_pointers

    def _gen_asm(self, string_pointers):
        """
        Generates the mod assembly code
        """
        if (self.verbose):
            print("Generating assembly code...")

        trampoline_obj = trampoline.Trampoline(string_pointers)
        mips_code = trampoline_obj.gen_asm()

        # Print assembly code if verbose
        if (self.verbose):
            print("Assembly code:")
            print(mips_code)

        # Write assembly code to file if debug
        if (self.debug):
            print("Writing assembly code to file...")
            with open("./out/mod.asm", "w+", encoding="utf-8") as file:
                file.write(mips_code)

        return mips_code

    def _gen_code_pnach(self, machine_code_bytes):
        """
        Generates the pnach object for the mod and hook code
        """
        if (self.verbose):
            print("Generating pnach file...")

        # Generate mod pnach code
        mod_chunk = pnach.Chunk(self.code_address, machine_code_bytes)
        mod_chunk.set_header(f"comment=Writing {len(machine_code_bytes)} bytes of machine code at {hex(self.code_address)}")

        # Print mod pnach code if verbose
        if (self.verbose):
            print("Mod pnach:")
            print(mod_chunk)

        # Generate pnach for function hook to jump to trampoline code
        hook_asm = f"j {self.code_address}\n"
        hook_code, count = self.assemble(hook_asm)

        hook_chunk = pnach.Chunk(self.hook_adr, hook_code)
        hook_chunk.set_header(f"comment=Hooking string load function at {hex(self.hook_adr)}")

        # Print hook pnach code if verbose
        if (self.verbose):
            print("Hook pnach:")
            print(hook_chunk)

        return mod_chunk, hook_chunk


    def generate_pnach_str(self, input_file, mod_name=None, author="Sly String Toolkit"):
        """
        Generates the mod pnach text from the given input file
        """
        # Generate the strings, asm code, and pnach files
        auto_strings_chunk, manual_sting_chunks, string_pointers = self._gen_strings_from_csv(input_file)
        trampoline_asm = self._gen_asm(string_pointers)
        trampoline_binary, count = self.assemble(trampoline_asm)
        mod_chunk, hook_chunk = self._gen_code_pnach(trampoline_binary)

        # Set the mod name (default is same as input file)
        if (mod_name is None or mod_name == ""):
            mod_name = os.path.splitext(os.path.basename(input_file))[0]

        # Set up pnach header lines
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        region_string = self.region.upper()
        header_lines = f"gametitle=Sly 2: Band of Thieves ({region_string})\n" \
            + f"comment={mod_name} by {author}\n\n" \
            + f"{mod_name} by {author}\n" \
            + "Pnach generated with Sly String Toolkit\n" \
            + "https://github.com/theonlyzac/sly-string-toolkit\n" \
            + f"date: {timestamp}\n"

        # Add all mod chunks to final pnach
        final_mod_pnach = pnach.Pnach(header=header_lines)
        final_mod_pnach.add_chunk(hook_chunk)
        final_mod_pnach.add_chunk(mod_chunk)
        final_mod_pnach.add_chunk(auto_strings_chunk)
        for chunk in manual_sting_chunks:
            final_mod_pnach.add_chunk(chunk)

        # Print final pnach if verbose
        if (self.verbose):
            print("Final mod pnach:")
            print(final_mod_pnach)

        if self.lang is None:
            return str(final_mod_pnach)

        # Add language check conditional to final pnach
        final_mod_pnach.add_conditional(0x2E9254, self.lang, 'eq')

        # Generate pnach which cancels the function hook by setting the asm back to the original
        cancel_hook_pnach = pnach.Pnach()
        cancel_hook_asm = "jr $ra\nlw $v0, 0x4($a0)"
        cancel_hook_bytes, count = self.assemble(cancel_hook_asm)

        # Keystone does this annoying thing where it always adds a dummy nop after a jump
        # so we need to trim out the middle 4 bytes
        cancel_hook_bytes = cancel_hook_bytes[:4] + cancel_hook_bytes[8:]

        cancel_hook_chunk = pnach.Chunk(self.hook_adr, cancel_hook_bytes,
            f"comment=Loading {len(cancel_hook_bytes)} bytes of machine code (hook cancel) at {hex(self.hook_adr)}...")
        # Add chunk and conditional to pnach
        cancel_hook_pnach.add_chunk(cancel_hook_chunk)

        # Add conditional to cancel the function hook if game is set to the wrong language
        cancel_hook_pnach.add_conditional(0x2E9254, self.lang, 'neq')

        if (self.verbose):
            print("Cancel hook pnach:")
            print(cancel_hook_pnach)

        return str(final_mod_pnach) + str(cancel_hook_pnach)

    def generate_pnach_file(self, input_file, output_dir="./out/", mod_name=None, author="Sly String Toolkit"):
        """
        Generates a mod pnach and writes it to a file
        """

        # Create the out folder if it doesn't exist
        if (not os.path.exists(output_dir)):
            if (self.verbose):
                print("Output directory doesn't exist, creating it...")
            os.mkdir(output_dir)

        # Set crc based on region
        crc = SLY2_NTSC_CRC if self.region == "ntsc" else SLY2_PAL_CRC

        # Set the mod name (default is same as input file)
        if (mod_name is None or mod_name == ""):
            mod_name = os.path.splitext(os.path.basename(input_file))[0]

        # Generate the pnach
        pnach_lines = self.generate_pnach_str(input_file, mod_name, author)

        # Write the final pnach file
        outfile = os.path.join(output_dir, f"{crc}.{mod_name}.pnach")
        with open(outfile, "w+", encoding="iso-8859-1") as f:
            f.write(pnach_lines)

        print(f"Wrote pnach file to {outfile}")


if __name__ == "__main__":
    print("Run the generator with 'python main.py'")
