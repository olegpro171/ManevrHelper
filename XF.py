import os
from os import path


file_name_length = 9


class XenonFile:
    DirEntry: os.DirEntry
    directory: str
    file_name: str

    time: str
    power:  str
    shut_down: str

    def __init__(self, DirEntry: os.DirEntry):
        # Store file path
        self.directory = os.path.dirname(DirEntry.path)  # Store the directory path
        self.file_name = os.path.basename(DirEntry.path)  # Store the file name
        self.DirEntry = DirEntry
        
        # Validate the file name format
        self.validate_file_name(DirEntry.path)

    def validate_file_name(self, file_path):
        # Extract the file name without the directory path
        file_name = os.path.basename(file_path)
        
        # Ensure the file name is 9 characters long
        if len(file_name) != 9:
            raise ValueError("File name must be exactly 9 characters long")
        
        # Ensure the name starts with "XE"
        if not file_name.startswith("XE"):
            raise ValueError("File name must start with 'XE'")
        
        # Ensure the next 7 characters are digits
        digits_part = file_name[2:]
        if not digits_part.isdigit():
            raise ValueError("The last 7 characters must be digits")
        
        # Parse the first 3 digits as time
        self.time = (digits_part[:3])
        
        # Parse the next 2 digits as power
        self.power = (digits_part[3:5])
        
        # Parse the last 2 digits as shut_down
        self.shut_down = (digits_part[5:])


class XenonFileSimple:
    file_name: str

    MoC: int
    state: int
    count: int

    def __init__(self, file_name: str, MoC: int, state: int, count: int):
        self.file_name = file_name

        self.MoC = MoC
        self.state = state
        self.count = count

    @property
    def directory(self):
        return os.path.dirname(self.file_name)