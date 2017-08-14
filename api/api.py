#!/usr/bin/env python
# coding=utf-8
import cgi
import json
import logging
import os
import random
import urllib2

import mutagen.mp3
from PIL import Image

import config


def get_current_song(stats_url, stats_stream):
    """
    Retruns current playing song - artist and title
    :param stats_url: url points to icecast stats url (JSON format)
    :param stats_stream: main stream to get info
    :return: string
    "Artist - Title"
    """
    try:
        stats = json.loads(urllib2.urlopen('http://radio1838.me:1838/status-json.xsl').read())
    except:
        logging.error('get_current_song: Can not open stats url \"%s\"', stats_url)
        return False
    if stats_stream not in stats:
        logging.error('get_current_song: Can not find stream \"%s\" in stats data', stats_stream)
        return False
    return stats[stats_stream]['title'].encode("utf-8")


def find_file(name, path):
    """
    Finds file in path
    :param name: file name
    :param path: path to recursive search
    :return:
        string with full file name (with path) if file found
        false - otherwise
    """
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def extract_cover(local_file, covers_dir, cover_name):
    """
    Extracts cover art from mp3 file
    :param local_file: file name (with path)
    :param covers_dir: path to store cover art files
    :param cover_name: name for extracted cover art file
    :rtype: bool
    :return:
        False - file not found or contains no cover art
        True - all ok, cover extracted
    """
    try:
        tags = mutagen.mp3.Open(local_file)
        data = ""
        for i in tags:
            if i.startswith("APIC"):
                data = tags[i].data
                break
        if not data:
            return False
        else:
            with open(covers_dir + cover_name, "w") as cover:
                cover.write(data)
                return True
    except:
        logging.error('extract_cover: File \"%s\" not found in %s', local_file, covers_dir)
        return False


def resize_image(image_file, new_size):
    """
    Resizes image keeping aspect ratio
    :param image_file: file name (with full path)
    :param new_size: new file max size
    :rtype bool
    :return:
        False - resize unsuccessful or file not found
        True - otherwise
    """
    try:
        img = Image.open(image_file)
    except:
        logging.error('resize_image: Can not open mage file \"%s\"', image_file)
        return False
    if max(img.size) > new_size:
        k = float(new_size) / float(max(img.size))
        new_img = img.resize(tuple([int(k * x) for x in img.size]), Image.ANTIALIAS)
        img.close()
        new_img.save(image_file)
    return True


def normalize_filename(filename):
    """
    Replaces special symbols in string. Replace rules described at replacements dictionary
    :param filename: string need to be normalized
    :return:
    returns normalized string
    """
    replacements = {"?": "!", "/": ","}
    for word, replace in replacements.items():
        filename = filename.replace(word, replace)
    return filename


def generate_xml(arguments):
    header = "Content-Type: application/xml; charset=UTF-8\n\n"
    template = 'templated_page.xml' if bool(arguments) else 'empty_page.xml'
    with open(template, 'r') as xml_file:
        return header + xml_file.read().format(**arguments)


if __name__ == '__main__':

    logging.basicConfig(filename=config.log_file, level=logging.INFO, format='[%(asctime)s] %(message)s')

    default_covers = []
    for (dirpath, dirnames, filenames) in os.walk(config.path['default']):
        default_covers.extend(filenames)
        break

    query_string = cgi.FieldStorage()

    if not bool(query_string):
        logging.warning('Mailformed request \"%s\"', query_string)
        tags = {}
    else:
        if 'artist' not in query_string and 'title' not in query_string:
            now_playing = get_current_song(config.url['stats'], config.stats_stream).split(' - ', 1)
            artist = now_playing[0]
            title = now_playing[1]
        else:
            artist = query_string['artist'].value
            title = query_string['title'].value

        file_name = normalize_filename(artist + ' - ' + title)

        mp3_file = file_name + '.mp3'
        art_file = file_name + '.jpg'

        local_file = find_file(mp3_file, config.path['music'])

        if not local_file:
            logging.error('File \"%s.mp3\" not found in %s', file_name, config.path['music'])
            art_url = config.url['default'] + random.choice(default_covers)
        elif os.path.isfile(config.path['covers'] + art_file):
            art_url = config.url['static'] + file_name + '.jpg'
        elif not extract_cover(local_file, config.path['covers'], art_file):
            art_url = config.url['default'] + random.choice(default_covers)
        else:
            resize_image(config.path['covers'] + art_file, config.cover_size)
            art_url = config.url['static'] + file_name + '.jpg'

        tags = {'arturl': cgi.escape(art_url),
                'artist': cgi.escape(artist),
                'title': cgi.escape(title),
                'album': 'Various',
                'size': config.cover_size}

    print generate_xml(tags)
