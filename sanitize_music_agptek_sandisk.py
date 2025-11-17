#!/usr/bin/env python

# Choose the directory where to to sanitize the music files
# TODO pass the directory in argument or better detect USB key and interactively choose the user
DIR_PATH: str = "/run/media/mil/AGP-A65/MUSIC"
TERMINAL_OUPUT: bool = True

# System requierement:
# ffmpeg

# Python requierement:
# dependencies = [
#   "mutagen",
# ]


import os
import subprocess
from mutagen.id3 import ID3
from mutagen.id3._frames import TPE1
from mutagen.oggvorbis import OggVorbis


def convert_to_mp3(input_file: str) -> tuple[str, str]:
    "Convert Opus to MP3 using ffmpeg"

    output_file = input_file.replace('.opus', '.mp3')
    command = 'ffmpeg -i "' + input_file + '" -map_metadata 0:s:0 "' + output_file + '"'
    error_msg = ''
    result = subprocess.run(command, shell=True, capture_output=False, text=True, check=False)
    if (result.stderr is not None and result.stderr.lower().find("error")):
        error_msg = result.stderr 
    os.remove(input_file)
    return output_file, error_msg


def normalize_tags(artist: str) -> str:
    """
    Truncate artist field between beginning and the first character '+' to
    keep the same artist on all the album. Arbitrarilly choose to keep only the
    first.
    """
    return artist.split("+")[0].strip()
    # pos_split = artist.find("+")
    # if pos_split != -1:
    #     new_artist = artist[:pos_split].rstrip()


def normalize_audio_files_tags_for_usb_player(directory: str) -> str:
    "In the current directory and subdirectory, normalize the tags for my AGPTEK music player. Remove the multiple artist split by char '+' in the artist field for ogg and mp3. Convert the opus to mp3, because my player cannot read them."

    errors = ""
    for root, _, files in os.walk(directory):
        print(f"Current directory : {files}") if TERMINAL_OUPUT else None
        for file in files:
            print(f"\t{file}") if TERMINAL_OUPUT else None
            fullpathfile = os.path.join(root, file)

            if str(fullpathfile).lower().endswith('.opus'):
                fullpathfile, error_msg = convert_to_mp3(fullpathfile)
                errors += error_msg

            if str(fullpathfile).lower().endswith('.mp3'):
                audioid3: ID3 = ID3(fullpathfile)
                artist = str(audioid3.get('TPE1', ''))
                new_artist = normalize_tags(artist)
                if new_artist != artist:
                    audioid3['TPE1'] = TPE1(encoding=3, text=[new_artist])
                    print("normalize mp3 artist") if TERMINAL_OUPUT else None
                    audioid3.save(v2_version=4)

            if str(fullpathfile).lower().endswith('.ogg'):
                audioogg: OggVorbis = OggVorbis(fullpathfile)
                # in ogg the key field have multiple value so they are list
                artist = str(audioogg.get('artist', '')[0])
                new_artist = normalize_tags(artist)
                if new_artist != artist:
                    audioogg['artist'] = new_artist
                    print("normalize ogg artist") if TERMINAL_OUPUT else None
                    audioogg.save()

    return errors 


if __name__ == "__main__":
    if os.path.isdir(DIR_PATH) and  os.access(DIR_PATH, os.R_OK):
        _ = normalize_audio_files_tags_for_usb_player(os.path.abspath(DIR_PATH))
        print("DONE sanitize_music_agptek_sandisky")
    else:
        print(f"ERROR no such directory\n{DIR_PATH}")
    

