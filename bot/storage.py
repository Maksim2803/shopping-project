import json
class Storage:
    def __init__(self,filename):
        self.filename = filename
    def load(self):
        try:
            with open(f"{self.filename}.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save(self, data):
        with open(f"{self.filename}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

