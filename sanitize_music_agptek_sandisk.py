#!/usr/bin/env python

# System requierement:
# ffmpeg

# Python requierement:
# mutagen
# python-python-ffmpeg

import os
from mutagen.id3 import TPE1, ID3
from mutagen.oggvorbis import OggVorbis
import ffmpeg


def normalize_artist(artist):
    "Truncate artist field between beginning and first '+' to keep the same artist on all the album"
    return artist.split("+")[0].strip()
    # pos_split = artist.find("+")
    # if pos_split != -1:
    #     new_artist = artist[:pos_split].rstrip()


def convert_to_mp3(input_file):
    "Convert Opus to MP3 using ffmpeg"

    output_file = input_file.replace('.opus', '.mp3')
    try:
        ffm = ffmpeg.FFmpeg().input(input_file).output(output_file)
        ffm.execute()
        os.remove(input_file)
        return output_file

    except ffmpeg.FFmpegError as e:
        print(f"Error converting : {e}")
        return input_file


def normalize_audio_files_tags_for_usb_player(directory):
    """
    In the current directory and subdirectory, normalize the tags for my
    AGPTEK music player
    """

    for root, _, files in os.walk(directory):
        for file in files:
            fullpathfile = os.path.join(root, file)

            if str(fullpathfile).lower().endswith('.opus'):
                fullpathfile = convert_to_mp3(fullpathfile)

            if str(fullpathfile).lower().endswith('.mp3'):
                audio = ID3(fullpathfile)
                artist = str(audio.get('TPE1', ''))
                new_artist = normalize_artist(artist)
                if new_artist != artist:
                    audio['TPE1'] = TPE1(encoding=3, text=[new_artist])
                    audio.save()

            if str(fullpathfile).lower().endswith('.ogg'):
                audio = OggVorbis(fullpathfile)
                # in ogg the key field have multiple value so they are list
                artist = str(audio.get('artist', '')[0])
                new_artist = normalize_artist(artist)
                if new_artist != artist:
                    audio['artist'] = new_artist
                    audio.save()


if __name__ == "__main__":
    normalize_audio_files_tags_for_usb_player(os.getcwd())
