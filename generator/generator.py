"""
Generator class which generates a pnach file from a CSV file.
"""
import os
from datetime import datetime
from typing import List, Tuple
import struct
import keystone
from generator import strings, trampoline, pnach
from utils import Assembler
from dataclasses import dataclass

@dataclass
class GameInfo:
    title: str
    crc: str
    hook_adr: int
    hook_delayslot: str
    lang_adr: int
    asm_adr: int
    strings_adr: int
    encoding: str
    #string_table: int

GAME_INFO = {
    2: {
        "ntsc": GameInfo(
            title="Sly 2: Band of Thieves (USA)",
            crc="07652DD9",
            hook_adr=0x13e380,
            hook_delayslot="lw $v0, 0x4($a0)",
            lang_adr=None,
            asm_adr=0x2E60B0,
            strings_adr=0x3C7980,
            encoding='iso-8859-1'
        ),
        "pal": GameInfo(
            title="Sly 2: Band of Thieves (Europe)",
            crc="FDA1CBF6",
            hook_adr=0x13e398,
            hook_delayslot="lw $v0, 0x4($a0)",
            lang_adr=0x2E9254,
            asm_adr=0x2ED500,
            strings_adr=0x3CF190,
            encoding='iso-8859-1'
        )
    },
    3: {
        "ntsc": GameInfo(
            title="Sly 3: Honor Among Thieves (USA)",
            crc="8BC95883",
            hook_adr=0x150648,
            hook_delayslot="lw $v0, 0x4($v1)",
            lang_adr=None,
            asm_adr=0x45af00,
            strings_adr=0x0F1050,
            encoding='UTF-16'
            #string_table=x47A2D8
        )#,
        #"pal": GameInfo(
            #title="Sly 3: Honour Among Thieves (Europe)",
            #hook_delayslot="lw $v0, 0x4($v1)",
            #encoding='UTF-16',
            #string_table=0x47B958
        #)
    }
}

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

    def __init__(self, game: int, region: str, lang: str = None, strings_address: int = None, code_address: int = None):
        """
        Initializes the generator with the specified region and addresses
        """
        # Set region
        self.region = region.lower()

        try:
            self.game_info = GAME_INFO[game][region]
        except KeyError as e:
            raise ValueError(f"Error: Game or region not supported ({game}/{region})")

        self.strings_adr = self.game_info.strings_adr if strings_address is None else strings_address
        self.code_address = self.game_info.asm_adr if code_address is None else code_address
        self.hook_adr = self.game_info.hook_adr
        self.lang_adr = self.game_info.lang_adr

        if lang is not None and region == "ntsc":
            print("Warning: Language selection is not supported for NTSC region, using English")
            self.lang = LANGUAGE_IDS["en"]
        else:
            self.lang = LANGUAGE_IDS[lang.lower()] if lang is not None else None

        # Ensure addresses are ints
        if isinstance(self.strings_adr, str):
            self.strings_adr = int(self.strings_adr, 16)
        if isinstance(self.code_address, str):
            self.code_address = int(self.code_address, 16)
        if isinstance(self.hook_adr, str):
            self.hook_adr = int(self.hook_adr, 16)

    @staticmethod
    def set_verbose(verbose: bool) -> None:
        """
        Sets the verbose flag
        """
        Generator.verbose = verbose
        if verbose:
            print("Verbose output enabled")

    @staticmethod
    def set_debug(debug: bool) -> None:
        """
        Sets the debug flag
        """
        Generator.debug = debug
        if debug:
            print("Debug output enabled")

    @staticmethod
    def assemble(asm_code: str) -> Tuple[bytes, int]:
        """
        Assembles the given assembly code to binary and converts it to a byte array
        """
        # Assemble the assembly code
        assembler = Assembler(keystone.KS_ARCH_MIPS, keystone.KS_MODE_MIPS32 + keystone.KS_MODE_LITTLE_ENDIAN)
        binary, count = assembler.assemble(asm_code)

        # Convert the binary to bytes
        machine_code_bytes = struct.pack('B' * len(binary), *binary)

        # Print machine code bytes if verbose
        if Generator.verbose:
            print(f"Assembled {count} bytes of machine code")
            print("Machine code bytes:")
            print(binary)

        # Write machine code bytes to file if debug
        if Generator.debug:
            print("Writing binary code to file...")
            with open("./out/mod.bin", "wb+") as file:
                file.write(machine_code_bytes)

        return machine_code_bytes, count

    def _gen_strings_from_csv(self, csv_file: str, csv_encoding: str = "utf-8", patch_format: str = "pnach") -> Tuple[pnach.Chunk, List[pnach.Chunk], List[Tuple[int, int]]]:
        """
        Generates the strings pnach and populate string pointers
        """
        if self.verbose:
            print(f"Reading strings from {csv_file} to 0x{self.strings_adr:X}...")

        # Ensure file exists
        if not os.path.isfile(csv_file):
            raise Exception(f"Error: File {csv_file} does not exist")

        out_encoding = self.game_info.encoding
        strings_obj = strings.Strings(csv_file, self.strings_adr, csv_encoding, out_encoding)
        auto_strings_chunk, manual_string_chunks, string_pointers = strings_obj.gen_pnach_chunks(patch_format)

        # Print string pointers if verbose
        if self.verbose:
            print("String pointers:")
            for string_id, string_ptr in string_pointers:
                print(f"ID: {hex(string_id)} | Ptr: {hex(string_ptr)}")
            print("Auto strings pnach:")
            print(auto_strings_chunk)
            print("Manual strings pnach:")
            print('\n'.join([str(chunk) for chunk in manual_string_chunks]))

        return auto_strings_chunk, manual_string_chunks, string_pointers

    def _gen_asm(self, string_pointers: list) -> str:
        """
        Generates the mod assembly code
        """
        if self.verbose:
            print("Generating assembly code...")

        trampoline_obj = trampoline.Trampoline(string_pointers)
        mips_code = trampoline_obj.gen_asm(self.game_info.hook_delayslot)

        # Print assembly code if verbose
        if self.verbose:
            print("Assembly code:")
            print(mips_code)

        # Write assembly code to file if debug
        if self.debug:
            print("Writing assembly code to file...")
            with open("./out/mod.asm", "w+", encoding="utf-8") as file:
                file.write(mips_code)

        return mips_code

    def _gen_code_pnach(self, machine_code_bytes: bytes, patch_format: str) -> Tuple[pnach.Chunk, pnach.Chunk]:
        """
        Generates the pnach object for the mod and hook code
        """
        if self.verbose:
            print("Generating pnach file...")

        # Generate mod pnach code
        mod_chunk = pnach.Chunk(self.code_address, machine_code_bytes, patch_format=patch_format)
        mod_chunk.set_header(f"Writing {len(machine_code_bytes)} bytes of machine code at {hex(self.code_address)}")

        # Print mod pnach code if verbose
        if self.verbose:
            print("Mod pnach:")
            print(mod_chunk)

        # Generate pnach for function hook to jump to trampoline code
        hook_asm = f"j {self.code_address}\n"
        hook_code, count = self.assemble(hook_asm)

        hook_chunk = pnach.Chunk(self.hook_adr, hook_code, patch_format=patch_format)
        hook_chunk.set_header(f"Hooking string load function at {hex(self.hook_adr)}")

        # Print hook pnach code if verbose
        if self.verbose:
            print("Hook pnach:")
            print(hook_chunk)

        return (mod_chunk, hook_chunk)


    def generate_patch_str(self, input_file: str, mod_name: str = None, author: str = "Sly String Toolkit", csv_encoding: str = "utf-8", patch_format: str = "pnach") -> str:
        """
        Generates the mod pnach text from the given input file
        """
        # Generate the strings, asm code, and pnach files
        auto_strings_chunk, manual_sting_chunks, string_pointers = self._gen_strings_from_csv(input_file, csv_encoding, patch_format=patch_format)
        trampoline_asm = self._gen_asm(string_pointers)
        trampoline_binary, count = self.assemble(trampoline_asm)
        mod_chunk, hook_chunk = self._gen_code_pnach(trampoline_binary, patch_format=patch_format)

        # Set the mod name (default is same as input file)
        if (mod_name is None or mod_name == ""):
            mod_name = os.path.splitext(os.path.basename(input_file))[0]

        # Set up pnach header lines
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gametitle= self.game_info.title
        header_lines = f"[{mod_name}]\n" \
            + f"author={author}\n" \
            + f"gametitle={gametitle}\n" \
            + "description=Generated with Sly String Toolkit\n" \
            + "https://github.com/theonlyzac/sly-string-toolkit\n" \
            + f"date={timestamp}\n"

        # Add all mod chunks to final pnach
        final_mod_patch = pnach.Pnach(header=header_lines, patch_format=patch_format)
        final_mod_patch.add_chunk(hook_chunk)
        final_mod_patch.add_chunk(mod_chunk)
        final_mod_patch.add_chunk(auto_strings_chunk)
        for chunk in manual_sting_chunks:
            final_mod_patch.add_chunk(chunk)

        # Print final pnach if verbose
        if self.verbose:
            print("Final mod pnach:")
            print(final_mod_patch)

        if self.lang is None:
            return str(final_mod_patch)

        # Add language check conditional to final pnach
        final_mod_patch.add_conditional(self.lang_adr, self.lang, 'eq')

        # Generate pnach which cancels the function hook by setting the asm back to the original
        cancel_hook_patch = pnach.Pnach(patch_format=patch_format)
        cancel_hook_asm = "jr $ra\nlw $v0, 0x4($a0)"
        cancel_hook_bytes, count = self.assemble(cancel_hook_asm)

        # Keystone does this annoying thing where it always adds a dummy nop after a jump
        # so we need to trim out the middle 4 bytes
        cancel_hook_bytes = cancel_hook_bytes[:4] + cancel_hook_bytes[8:]

        cancel_hook_chunk = pnach.Chunk(self.hook_adr, cancel_hook_bytes,
            f"Loading {len(cancel_hook_bytes)} bytes of machine code (hook cancel) at {hex(self.hook_adr)}...", patch_format=patch_format)
        # Add chunk and conditional to pnach
        cancel_hook_patch.add_chunk(cancel_hook_chunk)

        # Add conditional to cancel the function hook if game is set to the wrong language
        cancel_hook_patch.add_conditional(self.lang_adr, self.lang, 'neq')

        if self.verbose:
            print("Cancel hook pnach:")
            print(cancel_hook_patch)

        return str(final_mod_patch) + str(cancel_hook_patch)

    def generate_patch_file(self, input_file: str, output_dir: str = "./out/", mod_name: str = None, author: str = "Sly String Toolkit", csv_encoding: str = "utf-8", format: str = "pnach") -> None:
        """
        Generates a mod pnach and writes it to a file
        """

        # Create the out folder if it doesn't exist
        if not os.path.exists(output_dir):
            if self.verbose:
                print("Output directory doesn't exist, creating it...")
            os.mkdir(output_dir)

        # Set crc based on region
        crc = self.game_info.crc

        # Set the mod name (default is same as input file)
        if (mod_name is None or mod_name == ""):
            mod_name = os.path.splitext(os.path.basename(input_file))[0]

        # Generate the pnach
        patch_lines = self.generate_patch_str(input_file, mod_name, author, csv_encoding, format)

        # Write the final pnach file
        outfile = os.path.join(output_dir, f"{crc}.{mod_name}.{format}")
        with open(outfile, "w+", encoding="iso-8859-1") as f:
            f.write(patch_lines)

        print(f"Wrote pnach file to {outfile}")


if __name__ == "__main__":
    print("Run the generator with 'python main.py'")
