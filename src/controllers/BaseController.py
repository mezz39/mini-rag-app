from helpers import get_settings, Settings
import os
import string
import random
from pathlib import Path
class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = Path(__file__).resolve().parents[2] 
        self.files_dir = os.path.join(self.base_dir,"src", "assets", "files")

    def generate_random_string(self, length: int = 12) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k= length))