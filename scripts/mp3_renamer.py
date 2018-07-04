#!/usr/bin/env python
# coding=utf-8

import os
import time
import sys
import unicodedata
import platform

from mutagen.easyid3 import EasyID3


def get_tags(mp3_file):
    """
    Returns mp3 file's artist and title tags
    :param mp3_file: local filename (with path)
    :return:
    dictionary contained artist and title tags
    """
    audio = EasyID3(mp3_file)

    if 'artist' not in audio.keys() or 'title' not in audio.keys():
        return None

    return {'artist': audio['artist'], 'title': audio['title']}


def normalize_filename(filename):
    """
    Replaces special symbols in string. Replace rules described at replacements dictionary
    :param filename: string need to be normalized
    :return:
    returns normalized string
    """
    replacements = {"/": ",", "\"": "_", '"': "'", "*": "-", "?": "!"}
    for word, replace in replacements.items():
        filename = filename.replace(word, replace)
    return filename


if __name__ == '__main__':

    start_time = time.time()
    skipped = 0

    if len(sys.argv) == 1:
        print "Usage: mp3_renamer.py /path/to/check/ [--force-rename]"
        exit(1)
    else:
        root_dir = sys.argv[1]
        if len(sys.argv) == 3 and sys.argv[2] == '--force-rename':
            force_rename = True
            print "Force renaming enabled."
        else:
            force_rename = False

    search_pattern = '.mp3'
    mp3s = {}

    # generate list of all mp3s
    i = 0
    for root, dirs, files in os.walk(root_dir):
        for x in files:
            if x.endswith(search_pattern):
                mp3s[i] = {'path': root, 'filename': x}
                i += 1

    for x in mp3s:
        tags = get_tags('/'.join([mp3s[x]['path'], mp3s[x]['filename']]))

        if not tags:
            print "File {}/{} skipped due to missed tags.".format(mp3s[x]['path'], mp3s[x]['filename'])
            skipped += 1
            continue

        expected_name = normalize_filename(
            ''.join(tags['artist']).encode("utf-8") + ' - ' + ''.join(tags['title']).encode("utf-8") + search_pattern)
        local_name = mp3s[x]['filename']

        # Mac unicode filename normalize
        if platform.system() == 'Darwin':
            local_name = unicodedata.normalize('NFC', unicode(local_name, 'utf-8')).encode('utf-8')

        if not local_name == expected_name:
            print local_name, "=>", expected_name
            if force_rename is True or not os.path.exists(mp3s[x]['path'] + '/' + expected_name):
                try:
                    os.rename(mp3s[x]['path'] + '/' + mp3s[x]['filename'], mp3s[x]['path'] + '/' + expected_name)
                except Exception, e:
                    print "Can't rename file:", repr(e)
            else:
                print "File {}/{} already exists. Rename skipped. For rename those files use --force-rename option.".format(mp3s[x]['path'], expected_name)
                skipped += 1

    # Some stats
    print "{} files were checked, {} skipped (see above), {} seconds spent.".format(len(mp3s), skipped, round(time.time() - start_time, 2))