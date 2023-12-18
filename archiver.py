import json
from pathlib import Path
from fetcher import Fetcher


class Archiver():
    def __init__(self, blog_id):
        self.BASE_DIR = Path(__file__).resolve().parent
        self.SETTINGS_FILE_DIR = Path(self.BASE_DIR).joinpath("settings.json")
        self._check_settings()
        self.settings = self._load_settings()
        
        self.blog_id = blog_id
        self.download_dir = self.settings["SETTINGS"]["DOWNLOAD_DIR"]
        self.header = self.settings["SETTINGS"]["HEADERS"]

    def _check_settings(self):
        if not Path(self.SETTINGS_FILE_DIR).exists(): self._create_settings()

    def _create_settings(self):
        settings = {
            "SETTINGS": {
                "DOWNLOAD_DIR" : f"{self.BASE_DIR}",
                "HEADERS" : {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                }
            }
        }

        with open(self.SETTINGS_FILE_DIR, 'x') as file:
            json.dump(settings, file, indent=4, ensure_ascii=False)

    def _load_settings(self):
        with open(self.SETTINGS_FILE_DIR, 'r') as file:
            settings = json.load(file)

        return settings

    def change_settings(self, option, data):
        if option == "DOWNLOAD_DIR":
            self.settings["SETTINGS"]["DOWNLOAD_DIR"] = data
        elif option == "HEADERS":
            self.settings["SETTINGS"]["HEADERS"] = data
