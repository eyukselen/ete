import os
from typing import List


class FileManager:
    """This is a class to only hold list of open files"""
    def __init__(self, pth) -> None:
        self.root_path: str = pth or os.getcwd()
        self.open_files: List[str] = []
        self.files: List[str] = []
        self.current_file = ''
        self.selected_files: List[str] = []
