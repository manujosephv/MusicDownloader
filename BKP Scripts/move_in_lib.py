import difflib
import pandas as pd
import numpy as np
import os
from libpytunes import Library
import re
import shutil
from unidecode import unidecode
import codecs
import eyed3

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


ITUNES_PATH = "D:\Music\iTunes\iTunes Library.xml"
BACKUP_PATH = 'D:\Music Download'

def get_itunes_lib():
    path = backup_file(ITUNES_PATH, BACKUP_PATH)
    l = Library(path)
    songs = l.songs.items()
    dict_list = []
    for id, song in songs:
        song_dict = {}
        song_dict['artist'] = song.artist
        song_dict['title'] = song.name
        song_dict['genre'] = song.genre
        song_dict['album'] = song.album
        dict_list.append(song_dict)
    itunes_lib = pd.DataFrame(dict_list)
    itunes_lib['artist_stripped'] = itunes_lib.artist.apply(strip_ft)
    itunes_lib['title_stripped'] = itunes_lib.title.apply(strip_ft)
    itunes_lib['full_title_stripped'] = itunes_lib['artist_stripped'] +' - ' + itunes_lib['title_stripped']
    return itunes_lib

def backup_file(file_path, backup_path):
    logger.info('Copying iTunes xml to working directory')
    path, file_name = os.path.split(file_path)
    backup_full_path = os.path.join(backup_path,file_name)
    #Copy
    shutil.copy(file_path,backup_full_path)
    return backup_full_path

def strip_ft(artist):
    l = re.compile("\s\(?(ft(.)?|feat(.)?|featuring(.)?)\s").split(unicode(artist).lower())
    if len(l)>0:
        return l[0]
    else:
        return artist

def main():
	dict_list = {}
	folder = 'D:\Music Download\music-done'
	logger.info('Getting iTunes Library')
	itunes_df = get_itunes_lib()
	for root, dirs, files in os.walk(folder):
	    for name in files:
	        dict_file = {}
	        if name.endswith((".mp3")):
	            mp3 = eyed3.load(os.path.realpath(os.path.join(root,name)))
	            # print ("File: {}".format(name))
	            if mp3.tag:
	            	if mp3.tag.artist:
	            		if  mp3.tag.title:
		            		artist_stripped = strip_ft(mp3.tag.artist)
		            		title_stripped = strip_ft(mp3.tag.title)
		            		stripped_title = unicode(artist_stripped) + ' - ' + unicode(title_stripped)
		            		match = closest_match(stripped_title, itunes_df['full_title_stripped'].values)
		            		logger.debug(u'{} Match got as {}'.format(name,unidecode(match)))
		            		if match != 'No Match':
		            			logger.info(u'Moving {} to specified folder'.format(unidecode(name)))
		            			shutil.move(os.path.realpath(os.path.join(root,name)), os.path.realpath(os.path.join('D:\Music Download\in library',name)))






# billboard_chart_df['matched_title'] = billboard_chart_df['full_title_stripped'].apply(lambda x: closest_match(x,itunes_lib.full_title_stripped.values))


def closest_match(title,lib_full_title_list):
    match= difflib.get_close_matches(title,lib_full_title_list, cutoff=0.8)
#     print match
    if match:
        if len(match)>0:
            return match[0]
    else:
        return "No Match"


if __name__ == "__main__":
    main()