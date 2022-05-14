import re
import requests
import sys
import time

from lib import get_music, MusicMatchRecords, print_state
from urllib import parse


def parse_url(url):
    '''https://stackoverflow.com/questions/21584545/url-query-parameters-to-dict-python'''

    # Replace special char in netease's url
    url = url.replace('#', '_')
    result = dict(parse.parse_qsl(parse.urlsplit(url).query))
    if 'id' not in result:
        return -1
    return int(result['id'])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: {} <folder>'.format(sys.argv[0]))
        exit(1)

    musics = get_music(sys.argv[1])
    records = MusicMatchRecords(sys.argv[1] + '/music_match_records.json')

    for music in musics:
        if records.has(music) and records.get(music) != -1:
            continue

        u = input('Enter URL for {}: '.format(music))
        records.update(music, parse_url(u))
        print_state('DONE', music)
        print()
