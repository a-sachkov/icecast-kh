# What is it?

It is a .mp3 files cover art API written on Python.

## How does it work?

API accepts GET requests. Accepted variables:
* title - song title
* artist - song artist
* partner_token (optional) - authorization token

Simple description:

* API searches local directory for requested .mp3 file (using mask 'artist - title.mp3' as file name), extracts cover art from .mp3 file to .jpg, and returns XML file with link to download cover art file.

A little bit more complicated explanation what happened when API gets request:

* If the query is empty (contains no GET parameters) - returns empty XML
* If you have enabled authorization token (not null list of tokens in the configuration file) - checks the received token. If the token is wrong returns 401 Unauthorized.
* If variables artist and title are in the query - perform search at the local directory of mp3 files. If the request contains no artist and title variables - get now playing song title from the IceCast stats url.
    * If the file is not found - returns an empty XML
    * If the file is found, the sequence is as follows:
        * Check - are there any already ready cover for this file in the 'cover' directory? If there is - returns a link to it.
        * If the mp3 file has an embedded cover - extracts it to the directory with the covers, returns a link to it.
        * If the file directory contains album art file 'cover.jpg' - copies it to the directory of the albums artwork, returns a link to it.
        * If the directory of the artists has a cover with the name of the 'artist' variable - give a link to it.
        * If nothing is found, give a random image from a radio default covers directory.

### Installation:
Put api.py to your web server. Don't forget to make it executable. Rename `confit.py.dist` to `config.py` and fill it with your data. All descriptions you can find at `config.py.dist`

Example config file for nginx server you can find at `./nginx` directory.

If you're using IceCast-KH instead of IceCast - put [status-json.xsl](https://github.com/adel-s/radio/blob/master/icecast-kh/web/status-json.xsl) file to your IceCast-KH web directory (usually it's `/usr/local/share/icecast/web/`)