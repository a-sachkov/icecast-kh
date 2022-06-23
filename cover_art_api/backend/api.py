#!/usr/bin/env python
# coding=utf-8
import cgi
import hashlib
import logging
import os
import random
import urllib.request
from shutil import copyfile
import xml.etree.ElementTree as ET
import mutagen.mp3
from PIL import Image

import config


def get_now_playing(stats_url, stats_stream):
    """
    Returns current playing song - artist and title using auth to admin realm
    :param stats_url: url points to icecast stats url (xml)
    :param stats_stream: main stream to get info
    :return: string "Artist - Title"
    """
    auth_user = config.auth_user
    auth_pass = config.auth_pass

    passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, stats_url, auth_user, auth_pass)
    auth_handler = urllib.request.HTTPBasicAuthHandler(passman)
    opener = urllib.request.build_opener(auth_handler)
    urllib.request.install_opener(opener)

    try:
        res = urllib.request.urlopen(f"{stats_url}?mount={stats_stream}")
    except urllib.error.URLError as err:
        logging.error(f'get_current_song: Can not open stats url \"{stats_url}\": {err}')
        return False

    res_body = res.read()
    root = ET.fromstring(res_body)

    try:
        title = root.find(f"./source/[@mount='{stats_stream}']/title").text
    except IndexError as err:
        logging.error(f'get_current_song: Can not find stream \"{stats_stream}\" in stats data: {err}')
        return False

    return title


def find_file(name, path):
    """
    Finds file in path
    :param name: file name
    :param path: path to search recursively
    :return:
        string with path where file was found
        false - otherwise
    """
    for root, dirs, files in os.walk(path):
        if name in files:
            return root


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
        logging.error('Can not open image: \"%s\"', image_file)
        return False

    if max(img.size) != new_size:
        k = float(new_size) / float(max(img.size))
        new_img = img.resize(tuple([int(k * x) for x in img.size]), Image.ANTIALIAS)
        img.close()
        new_img.save(image_file)
    return True


def generate_album_art(local_path, album_cover_path, album_cover_name):
    """
    Searches album cover art at album arts path, if not found tries to generate it
    :param local_path:
    :param album_cover_path:
    :param album_cover_name:
    :rtype bool
    :return:
        False - no cover art found neither in local path nor at albums cover arts path
        True - otherwise
    """

    if os.path.isfile(album_cover_path + hashlib.md5(local_path.encode('utf-8')).hexdigest() + '.jpg'):
        return True
    elif os.path.isfile('/'.join([local_path, album_cover_name])):
        try:
            copyfile('/'.join([local_path, album_cover_name]), album_cover_path + hashlib.md5(local_path.encode('utf-8')).hexdigest() + '.jpg')
            return True
        except:
            return False
    return False


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


# TODO: cleanup this mess
def generate_page(arguments):
    """
    Generates page from template
    :param arguments:
    :return:
        xml file
    """
    header = "Content-Type: application/xml; charset=UTF-8\n\n"
    template = 'templated_page.xml' if bool(arguments) else 'empty_page.xml'
    with open(template, 'r') as xml_file:
        return header + xml_file.read().format(**arguments)


if __name__ == '__main__':

    logging.basicConfig(filename=config.path['log'], level=logging.INFO, format='[%(asctime)s] %(message)s')

    default_covers = []
    for (dirpath, dirnames, filenames) in os.walk(config.path['default']):
        default_covers.extend(filenames)
        break

    query_string = cgi.FieldStorage()

    if not query_string:
        logging.warning('Mailformed request \"%s\"', query_string)
        tags = {}
    elif config.tokens and ('partner_token' not in query_string or query_string['partner_token'].value not in config.tokens):
        logging.error('Unauthorized request: \"%s\"', query_string)
        header = "Status: 403 Forbidden\n\n"
        print(header)
    else:
        if 'artist' not in query_string and 'title' not in query_string:
            stream = config.default_stream if 'stream' not in query_string else query_string['stream'].value
            now_playing = get_now_playing(config.url['stats'], stream).split(' - ', 1)
            artist = now_playing[0]
            title = now_playing[1]
        else:
            artist = query_string['artist'].value
            title = query_string['title'].value

        file_name = normalize_filename(artist + ' - ' + title)

        mp3_file = file_name + '.mp3'
        art_file = file_name + '.jpg'
        local_file = find_file(mp3_file, config.path['music'])

        # there is no file you're looking for
        if not local_file:
            logging.error('File \"%s.mp3\" not found in %s', file_name, config.path['music'])
            art_url = config.url['default'] + random.choice(default_covers)
        else:
            # we already got an image for file
            if os.path.isfile(config.path['covers'] + art_file):
                art_url = config.url['static'] + art_file

            # wile has cover
            elif extract_cover('/'.join([local_file, mp3_file]), config.path['covers'], art_file):
                resize_image(config.path['covers'] + art_file, config.cover_size)
                art_url = config.url['static'] + file_name + '.jpg'

            # we have album cover
            elif generate_album_art(local_file, config.path['albums_covers'], config.files['cover']):
                art_url = config.url['albums_covers'] + hashlib.md5(local_file.encode('utf-8')).hexdigest() + '.jpg'

            # we have artist cover
            elif os.path.isfile(config.path['artists_covers'] + artist + '.jpg'):
                resize_image(config.path['artists_covers'] + artist + '.jpg', config.cover_size)
                art_url = config.url['artists_covers'] + artist + '.jpg'

            # return one of default covers
            else:
                art_url = config.url['default'] + random.choice(default_covers)

        tags = {'arturl': art_url,
                'artist': artist,
                'title': title,
                'album': 'Various',
                'size': config.cover_size}

        print(generate_page(tags))
