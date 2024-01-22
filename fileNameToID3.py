import os
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, TDRC, TCON, TRCK

def setTags(directory, date, genre):
    for filename in os.listdir(directory):
        title = os.path.splitext(filename)[0]

        tracknumber = title.split(". ", 1)[0]
        title = title.split(". ", 1)[1]

        pathfromhere = os.path.join(directory, filename)
        print("Full Path: " + pathfromhere)

        pathfromheresplit = os.path.normpath(pathfromhere).split(os.sep)
        artist = pathfromheresplit[0]
        album = pathfromheresplit[1]

        tags = ID3(pathfromhere)

        tags.add(TIT2(encoding=3, text=title))
        tags.add(TALB(encoding=3, text=album))
        tags.add(TPE1(encoding=3, text=artist))
        tags.add(TPE2(encoding=3, text=artist))
        tags.add(TRCK(encoding=3, text=str(tracknumber)))
        tags.add(TDRC(encoding=3, text=date))
        tags.add(TCON(encoding=3, text=genre))
        tags.setall('COMM', []) # Remove comments
        tags.save()

        print("New Tags: \n" + tags.pprint())

def resetTags(directory):
    for filename in os.listdir(directory):
        pathfromhere = os.path.join(directory, filename)

        tags = ID3(pathfromhere)
        print("Old Tags: \n" + tags.pprint())

        tags.delete()
        tags.save()

"""
For this to work, the files should be titled: 1. XXX.mp3
"""

while (0 != 1):
    DIRECTORY = input("Path Of Album From Here: ")
    # resetTags(DIRECTORY)

    DATE = input("Date Published: ")
    GENRE = input("Genre: ")
    setTags(DIRECTORY, DATE, GENRE)
    print("")