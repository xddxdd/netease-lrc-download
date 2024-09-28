import os
import re
import requests
import sys
import time

from lib import get_music, LrcOutput, MusicMatchRecords, print_state



def parse_lrc(lrc):
    result = {}
    for line in lrc.split('\n'):
        timestamps = []
        r = re.match(r'^\[(\d+):(\d+)\.(\d+)\](.+)$', line)
        while r:
            timestamp_ms = int(r[1]) * 60000 + \
                int(r[2]) * 1000 + int(int(r[3])
                                       * 1000 / (10 ** len(r[3])))
            timestamps.append(timestamp_ms)
            line = r[4].strip()
            r = re.match(r'^\[(\d{2}):(\d{2})\.(\d{2})\](.+)$', line)

        # Remove punctuations at beginning & end
        line = re.sub(r'^[^\w](.*)[^\w]+$', r'\1', line)

        for t in timestamps:
            result[t] = line

    # Filter out pure music
    if len(result) <= 1:
        return {}

    return result

# # Complex mechanism by recording state of two lyrics
# def merge_lyrics(lrc, tlrc):
#     result = {}
#     state_timestamp_ms = -1
#     state_lrc = ''
#     state_tlrc = ''

#     timestamps = sorted(list(lrc.keys()) + list(tlrc.keys()))
#     for t in timestamps:
#         if t <= state_timestamp_ms:
#             continue

#         changed = False

#         if t in lrc and lrc[t] != '':
#             state_lrc = lrc[t]
#             changed = True

#         if t in tlrc and tlrc[t] != '':
#             state_tlrc = tlrc[t]
#             changed = True

#         if not changed:
#             continue

#         if state_tlrc != '':
#             result[t] = '{}【{}】'.format(state_lrc, state_tlrc)
#         else:
#             result[t] = state_lrc

#     return result

# Simple mechanism by merging timestamps


def merge_lyrics(lrc, tlrc):
    result = {}
    timestamps = sorted(list(lrc.keys()) + list(tlrc.keys()))
    for t in timestamps:
        lrc_line = lrc[t] if t in lrc else ''
        tlrc_line = tlrc[t] if t in tlrc else ''

        if lrc_line and tlrc_line:
            result[t] = '{}【{}】'.format(lrc_line, tlrc_line)
        elif lrc_line:
            result[t] = lrc_line
        elif tlrc_line:
            result[t] = tlrc_line
        else:
            pass

    return result


def generate_lrc(lrc):
    result = ''
    for t, l in lrc.items():
        result += '[{:02d}:{:02d}.{:02d}]{}\n'.format(
            int(t / 60000), int(t % 60000 / 1000), int(t % 1000 / 10), l)
    return result


def get_lrc(id):
    if id is None:
        return None

    url = 'https://music.163.com/api/song/lyric'
    params = {'id': id, 'lv': -1, 'kv': -1, 'tv': -1}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    response = response.json()
    if response['code'] != 200:
        return None

    if 'lrc' in response:
        lrc = parse_lrc(response['lrc']['lyric'])
    else:
        lrc = {}

    if 'tlyric' in response:
        tlrc = parse_lrc(response['tlyric']['lyric'])
    else:
        tlrc = {}

    return generate_lrc(merge_lyrics(lrc, tlrc))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: {} <folder>'.format(sys.argv[0]))
        exit(1)

    musics = get_music(sys.argv[1])
    records = MusicMatchRecords(sys.argv[1] + '/music_match_records.json')

    output = LrcOutput(sys.argv[1])

    for music in musics:
        if not records.has(music):
            continue
        if output.has_lrc(music):
            continue

        print_state('DOWNLOAD', music)
        id = records.get(music)
        if id == -1:
            output.no_lrc(music)
            print_state('NONE', music)
            continue

        time.sleep(0.5)
        lrc = get_lrc(id)

        if lrc == '' or lrc is None:
            output.no_lrc(music)
            print_state('NONE', music)
        else:
            output.write_lrc(music, lrc)
            print_state('DONE', music)

        print()
