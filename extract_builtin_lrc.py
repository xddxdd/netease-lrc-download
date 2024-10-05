import functools
import multiprocessing
import os
import re
import subprocess
from typing import Optional
import requests
import sys
import time

from lib import get_music, LrcOutput, MusicMatchRecords, print_state


def get_lyric(filename: str) -> Optional[str]:
    result = subprocess.run(
        ["ffmpeg", "-i", filename, "-f", "ffmetadata", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        print(f"FFmpeg returned error {result.returncode}: {result.stderr}")
        return None

    # States: SEARCH, EXTRACT, DONE
    state = "SEARCH"
    lyric_text = ""
    for line in result.stdout.decode("utf-8", "ignore").splitlines():
        line = line.strip()
        if state == "SEARCH":
            if line.startswith("LYRICS="):
                line = line[len("LYRICS=") :]
                state = "EXTRACT"
        if state == "EXTRACT":
            if line.endswith("\\"):
                lyric_text += line[:-1] + "\n"
            else:
                lyric_text += line + "\n"
                state = "DONE"
        if state == "DONE":
            break
    return lyric_text if lyric_text else None


def check_music(output: LrcOutput, music):
    print_state("EXTRACT", music)
    lyric = get_lyric(os.path.join(sys.argv[1], music))
    if lyric:
        music_name = ".".join(music.split(".")[:-1])
        output.write_lrc(music_name, lyric)
        print_state("SAVED", music, True)
    else:
        pass
        # print_state("NONE", music, True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {} <folder>".format(sys.argv[0]))
        exit(1)

    musics = get_music(sys.argv[1], True)

    output = LrcOutput(sys.argv[1])

    pool = multiprocessing.Pool()

    pool.map(functools.partial(check_music, output), musics)
