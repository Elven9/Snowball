import json

class Simple_Cache:
    def __init__(self, on_disk_file="bbs.cache.json") -> None:
        # check if file exists
        # if yes, load it
        self.on_disk_file = on_disk_file
        try:
            with open(self.on_disk_file, "r") as f:
                self.cache = json.load(f)
        except FileNotFoundError:
            self.cache = {}

    def check_exist(self, key: str) -> bool:
        return key in self.cache

    def set_exist(self, key: str) -> None:
        self.cache[key] = ""

        # Write to disk
        with open(self.on_disk_file, "w") as f:
            json.dump(self.cache, f)

class Simple_Keyword:
    def __init__(self) -> None:
        self.on_disk_file = "bbs.keyword.json"
