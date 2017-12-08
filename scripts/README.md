### What?
Python script for renaming mp3 files in directory (with subdirs) by mask: `%artist% - %title%.mp3`

Works fast AF:

    adel@adel:~$ ./mp3_renamer.py ~/Music/Radio/
    4380 files were checked, 8.23 seconds spent.

### Usage:
mp3_renamer.py /path/to/search/mp3s/

Before renaming script checks is there a file with same name? If yes - file won't be renamed.
To override this you may use option --force-rename

Tested at *nix and macos. For MacOS systems added `normalization` for unicode file names due to MacOS special kind of `decomposed UTF-8` to store filenames.`

### Limitations:
File MUST contain `artist` and `title` tags.