import os
import json


class MusicMatchRecords:
    def __init__(self, db_path):
        self.db_path = db_path
        if os.path.exists(self.db_path):
            self.db_data = json.loads(open(self.db_path, "r").read())
        else:
            self.db_data = {}

    def _atomic_write(self):
        with open(self.db_path + ".tmp", "w") as f:
            json.dump(self.db_data, f, ensure_ascii=False, indent=2)
        os.rename(self.db_path + ".tmp", self.db_path)

    def has(self, music):
        return music in self.db_data

    def get(self, music):
        return self.db_data[music]

    def update(self, music, id):
        self.db_data[music] = id
        self._atomic_write()


class LrcOutput:
    def __init__(self, folder):
        self.folder = folder

    def has_lrc(self, music):
        lrc_filename = os.path.join(self.folder, f"{music}.lrc")
        nolrc_filename = os.path.join(self.folder, f"{music}.nolrc")
        return os.path.exists(lrc_filename) or os.path.exists(nolrc_filename)

    def write_lrc(self, music, lrc):
        lrc_filename = os.path.join(self.folder, f"{music}.lrc")
        nolrc_filename = os.path.join(self.folder, f"{music}.nolrc")
        with open(lrc_filename, "w") as f:
            f.write(lrc)

        if os.path.exists(nolrc_filename):
            os.unlink(nolrc_filename)

    def no_lrc(self, music):
        nolrc_filename = os.path.join(self.folder, f"{music}.nolrc")
        with open(nolrc_filename, "w") as f:
            f.write("PLACEHOLDER")


def get_music(folder, keep_extension: bool = False):
    extensions = ["mp3", "wav", "flac", "ncm"]

    result = os.listdir(folder)
    result = [
        (x if keep_extension else ".".join(x.split(".")[:-1]))
        for x in result
        if x.split(".")[-1].lower() in extensions
    ]
    return result


def print_state(state, music, newline: bool = False):
    print("[{}] {}".format(state.rjust(8), music), end=("\n" if newline else "\r"))
