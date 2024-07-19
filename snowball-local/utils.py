import json

class Simple_Cache:
    def __init__(self, on_disk_file="bbs.cache.json") -> None:
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
    def __init__(self, on_disk_file="bbs.keyword.json") -> None:
        self.on_disk_file = on_disk_file

        try:
            with open(self.on_disk_file, "r") as f:
                self.keyword = json.load(f)
        except FileNotFoundError:
            self.keyword = {}

    def add_user_to_keyword(self, user_id: int, keyword: str) -> None:
        if keyword not in self.keyword:
            self.keyword[keyword] = []
        if user_id not in self.keyword[keyword]:
            self.keyword[keyword].append(user_id)

        # Write to disk
        with open(self.on_disk_file, "w") as f:
            json.dump(self.keyword, f)

    def remove_user_from_keyword(self, user_id: int, keyword: str) -> None:
        if keyword in self.keyword:
            if user_id in self.keyword[keyword]:
                self.keyword[keyword].remove(user_id)

            if self.keyword[keyword] == []:
                self.keyword.pop(keyword, None)

            # Write to disk
            with open(self.on_disk_file, "w") as f:
                json.dump(self.keyword, f)

    def get_users_from_text(self, text: str) -> list[int]:
        user_ids = set()
        for keyword in self.keyword:
            if keyword in text:
                user_ids.update(self.keyword[keyword])

        return list(user_ids)
