from pathlib import Path
from PIL import Image
import re
import json
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, TDRC, TCON, TRCK, APIC
import mutagen.mp3

def toCaps(str):
    words = str.split(" ")
    for i in range(len(words)):
        if ("feat" in words[i]): # Skip case
            continue
        hasUpper = False # If the word already has an uppercase somewhere don't capitalize it
        for j in range(len(words[i])):
            if (words[i][j].isupper()):
                hasUpper = True
                break
        if (not hasUpper):
            for j in range(len(words[i])):
                if words[i][j].isalpha(): # Find the first alphabetic character
                    words[i] = words[i].replace(words[i][j], words[i][j].upper(), 1)
                    break
    return " ".join(word for word in words)

def legalizeFileName(file_name):
    # Don't allow illegal characters in file/folder names
    exclude = "/|<>:?*\\\""
    file_name = "".join(x for x in file_name if x not in exclude)
    file_name = re.sub(' +', ' ', file_name) # Remove multiple spaces
    file_name = toCaps(file_name) # This is done here to save a call to another function each time
    return file_name

while 1:
    URL = input("URL: ") # This should now work with track links as well
    genre = input("Genre (optional, leave blank to skip): ")

    print("Fetching...")
    try:
        page = requests.get(URL, timeout=10)
    except:
        print("Please enter a valid URL.") # If the URL doesn't begin with https:// or other issues
        continue
    if page.status_code != 200: # OK status code
        print("The page was not found.")
        continue

    html = BeautifulSoup(page.content, "html.parser")
    tracks = {}

    track_urls = []
    unavailable_track_urls = []
    scripts = html.find_all("script", attrs={"crossorigin": "anonymous"})
    for script in scripts: # This realistically only loops once because there is only one script with 'data-band' as an attribute
        if 'data-band' in script.attrs: # This tag is at the beginning of the line
            tracks_json = json.loads(script.attrs.get('data-tralbum'))
            track_infos = tracks_json.get('trackinfo')
            for track_info in track_infos:
                try:
                    track_url = track_info.get('file').get('mp3-128')
                    track_urls.append(track_url)
                except:
                    unavailable_track_urls.append(track_infos.index(track_info)) # Will add the index of the unavailable track (track number minus 1)
                    continue

    track_table = html.find(id="track_table")
    # Add all of the track titles as tracks in the dictionary
    track_titles = track_table.find_all("span", class_="track-title")
    for i in range(len(track_titles)):
        if (i not in unavailable_track_urls): # Skip the unavailable tracks
            tracks[i+1] = track_titles[i].text.strip()

    name_section = html.find(id="name-section")
    album = name_section.find(class_="trackTitle").text.strip() # Misnomer on their end
    artist = name_section.find("a").text.strip() # The artist name is stored in a hyperlink

    album_data = html.find(class_="tralbumData tralbum-credits")
    # Search for the first occurance of a year in the album credits
    date = re.findall(r".*[1-2][0-9]{3}", album_data.text.strip())[0] # For the full date
    year = re.findall(r"[1-2][0-9]{3}", album_data.text.strip())[0] # For the year only

    album_image = html.find(class_="popupImage")
    album_image_lq = album_image.attrs.get('href') # For lower resolution thumbnail
    album_image_hq = album_image.find_all("img")[0].attrs.get('src') # For higher resolution original
    img = Image.open(urlopen(album_image_hq)).tobytes()

    # Create the subdirectories
    dir = legalizeFileName(artist) + "/" + legalizeFileName(album) + "/"
    Path(dir).mkdir(parents=True, exist_ok=True)

    for tracknumber in tracks: # tracks[tracknumber] is the name of the current track

        current_track_url = track_urls[list(tracks).index(tracknumber)]
        file_name = dir + str(tracknumber) + ". " + legalizeFileName(tracks[tracknumber]) + ".mp3"
        print("Downloading track: " + file_name)

        download = requests.get(current_track_url, timeout=10)
        with open(file_name, "wb") as output:
            output.write(download.content)
        
        # Create the ID3 header if it's missing
        try:
            tags = ID3(file_name)
        except:
            tags = mutagen.File(file_name)
            tags.add_tags()
            tags.save(file_name, v1=2)
            tags = ID3(file_name)

        # Set the tags
        tags.add(TIT2(encoding=3, text=toCaps(tracks[tracknumber])))
        tags.add(TALB(encoding=3, text=toCaps(album)))
        tags.add(TPE1(encoding=3, text=toCaps(artist)))
        tags.add(TPE2(encoding=3, text=toCaps(artist)))
        tags.add(TDRC(encoding=3, text=year))
        tags.add(TRCK(encoding=3, text=str(tracknumber)))
        tags.add(TCON(encoding=3, text=genre))
        tags.add(APIC(encoding=3, mime="image/jpeg", type=3, data=img)) # Does this even work?
        tags.setall('COMM', []) # Remove any pre-existing comments
        tags.save()
    
    print("All tracks downloaded.")
