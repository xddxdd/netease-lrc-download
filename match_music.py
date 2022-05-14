import re
import requests
import sys
import time

from lib import get_music, MusicMatchRecords, print_state


def levenshtein_distance(s1, s2):
    '''https://stackoverflow.com/questions/2460177/edit-distance-in-python'''
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(
                    1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def get_keywords(filename):
    # Replace special characters
    filename = filename.replace('\xa0', ' ')
    filename = filename.replace(' - ', ' ')

    elements = []
    for element in filename.split(' '):
        if element == '':
            continue

        if element not in elements:
            elements.append(element)

    return ' '.join(elements)


def extract_artist_title(filename):
    try:
        s = filename.split(' - ', 2)
        return (s[0], s[1])
    except:
        return (None, filename)


def auto_match_netease_entry(songs, artist, title):
    for song in songs:
        artists = [x['name'] for x in song['artists']]
        name = song['name']

        if artist != None and not all([a in artist for a in artists]):
            continue

        if name.strip().lower() != title.strip().lower():
            continue

        return [song]

    return []


def select_netease_entry(songs, music, target_artist, target_title):
    print_state('MANUAL', music)
    print()

    def distance(song):
        artists = ' '.join([x['name'] for x in song['artists']])
        artists_sorted = ' '.join(sorted(artists.split(' ')))
        target_artist_sorted = ' '.join(sorted(target_artist.split(' ')))

        name = song['name']
        return levenshtein_distance(artists_sorted + ' - ' + name,
                                    target_artist_sorted + ' - ' + target_title)

    songs = sorted(songs, key=distance)
    for i, song in enumerate(songs):
        artists = ' '.join([x['name'] for x in song['artists']])
        print('{}. {} - {} ({}:{}, {})'.format(i, artists, song['name'], int(
            song['duration'] / 60000), int(song['duration'] % 60000 / 1000), distance(song)))

    try:
        id = int(input('Select song: '))
    except KeyboardInterrupt:
        exit(0)
    except:
        id = -1
    if id < 0 or id >= len(songs):
        return None

    return [songs[id]]


def search_netease(keywords, music, artist, title, interactive):
    url = 'https://music.163.com/api/search/get/'
    params = {'s': keywords, 'type': 1, 'limit': 50}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    response = response.json()
    if response['code'] != 200:
        return None

    if 'result' not in response:
        return None
    if 'songs' not in response['result']:
        return None

    response = response['result']['songs']
    if len(response) > 1:
        auto_match = auto_match_netease_entry(response, artist, title)
        if len(auto_match) > 0:
            return auto_match

    # Allow skipping uncertain music on first pass
    if len(response) > 1 and interactive:
        return select_netease_entry(response, music, artist, title)

    return response


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: {} <folder>'.format(sys.argv[0]))
        exit(1)

    musics = get_music(sys.argv[1])
    interactive_queue = []

    records = MusicMatchRecords('music_match_records.json')

    def process_music(music, interactive):
        if records.has(music):
            print_state('EXIST', music)
            return

        time.sleep(0.5)
        print_state('SEARCH', music)

        artist, title = extract_artist_title(music)
        kw = get_keywords(music)
        song = search_netease(kw, music, artist, title, interactive)

        if song is None or len(song) == 0:
            print_state('EMPTY', music)
            records.update(music, -1)
            return

        elif len(song) > 1 and not interactive:
            print_state('MULTIPLE', music)
            interactive_queue.append(music)
            return

        song = song[0]
        records.update(music, song['id'])
        print_state('DONE', music)

    # for music in musics:
    #     process_music(music, False)
    #     print()

    # for music in interactive_queue:
    #     process_music(music, True)
    #     print()

    for music in musics:
        process_music(music, True)
        print()
