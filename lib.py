import os
import json


class MusicMatchRecords:
    def __init__(self, db_path):
        self.db_path = db_path
        if os.path.exists(self.db_path):
            self.db_data = json.loads(open(self.db_path, 'r').read())
        else:
            self.db_data = {}

    def _atomic_write(self):
        with open(self.db_path + '.tmp', 'w') as f:
            json.dump(self.db_data, f, ensure_ascii=False, indent=2)
        os.rename(self.db_path + '.tmp', self.db_path)

    def has(self, music):
        return music in self.db_data

    def get(self, music):
        return self.db_data[music]

    def update(self, music, id):
        self.db_data[music] = id
        self._atomic_write()


def get_music(folder):
    extensions = ['mp3', 'wav', 'flac', 'ncm']

    result = os.listdir(folder)
    result = ['.'.join(x.split('.')[:-1])
              for x in result if x.split('.')[-1].lower() in extensions]
    return result


def print_state(state, music):
    print('[{}] {}'.format(state.rjust(8), music), end='\r')
