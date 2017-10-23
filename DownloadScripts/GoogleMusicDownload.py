import pandas as pd
from gmusicapi import Mobileclient
from MusicTools import MusicTools
from MusicTools import closest_match, get_itunes_lib, strip_ft
from unidecode import unidecode
import codecs
import os

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


import json
### LOADING THE CONFIG VARIABLES FROM FILE
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except:
    with open('../config.json', 'r') as f:
        config = json.load(f)

APP_PASSWORD = config['GOOGLEMUSIC']['APP_PASSWORD']
USER_NAME = config['GOOGLEMUSIC']['USER_NAME']
DUMP_FILE_NAME = os.path.join(config['DEFAULT']['ROOT'],config['GOOGLEMUSIC']['DUMP_FILE_NAME']) 
LAST_READ_FILE_NAME = os.path.join(config['DEFAULT']['ROOT'],config['GOOGLEMUSIC']['LAST_READ_FILE_NAME'])
DOWNLOAD_FAILED_FILE_NAME = os.path.join(config['DEFAULT']['ROOT'],config['GOOGLEMUSIC']['DOWNLOAD_FAILED_FILE_NAME'])

new_end = ''

def get_thumbs_up_list():

    thumbs_up_list = []
    end = ''
    with codecs.open(LAST_READ_FILE_NAME,encoding='utf-8') as f:
        #Skipping first line
        next(f)
        for line in f:
            end = line
    logger.info(u'Searching till {}'.format(end))
    count = 0
    global new_end
    with codecs.open(DUMP_FILE_NAME, encoding='utf-8') as f:
        #Skipping first line
        next(f)
        for line in f:
            if end in line:
                break
            if count == 0:
                new_end = line
                count = count+1
            song_dict={}
            logger.debug(line)
            try:
                line = unidecode(line)
            except UnicodeDecodeError:
                logger.warning("Unicode Error when decoding {}".format(line))

            logger.debug(line)
            parts = line.split(' - ')
            logger.debug(parts)
            song_dict['artist'] = parts[0].lstrip()
            song_dict['title'] = parts[1].rstrip()
            # logger.debug(song_dict)
            thumbs_up_list.append(song_dict)
    logger.debug(thumbs_up_list)
    logger.info('{} songs from Thumbs Up List'.format(len(thumbs_up_list)))
    if len(thumbs_up_list)>0:
        thumbs_up_df = pd.DataFrame(thumbs_up_list)
        thumbs_up_df['artist_stripped'] = thumbs_up_df.artist.apply(strip_ft)
        thumbs_up_df['title_stripped'] = thumbs_up_df.title.apply(strip_ft)
        thumbs_up_df['full_title_stripped'] = thumbs_up_df['artist_stripped'] +' - ' + thumbs_up_df['title_stripped']
    else:
        thumbs_up_df = pd.DataFrame()
    return thumbs_up_df

#Not used now. Getting Lib from iTunes
def get_lib_from_googlemusic():
    api = Mobileclient(debug_logging=False)
    logged_in = api.login(email=USER_NAME, password=APP_PASSWORD, locale='en_US', android_id=Mobileclient.FROM_MAC_ADDRESS)
    lib = api.get_all_songs()
    lib_list = []
    for song in lib:
        song_dict={}
        song_dict['artist'] = song['artist']
        # song_dict['album'] = song['album']
        song_dict['title'] = song['title']
        lib_list.append(song_dict)
    return pd.DataFrame(lib_list)

def get_songs_to_be_downloaded():
    logger.info('Getting the Songs from Exported txt file...')
    thumbs_up_df = get_thumbs_up_list()
    if len(thumbs_up_df.index)>0:
        logger.info('Getting all the songs in the library...')
        lib_df = get_itunes_lib()
        lib_df['full_title'] = lib_df['artist'] +' - '+ lib_df['title']
        thumbs_up_df['full_title'] = thumbs_up_df['artist'] +' - '+ thumbs_up_df['title']
        logger.info('Finding out the liked songs which are not currently in the library...')
        thumbs_up_df['matched_title'] = thumbs_up_df['full_title_stripped'].apply(lambda x: closest_match(x,lib_df.full_title_stripped.values))
        result = thumbs_up_df[thumbs_up_df['matched_title']=='No Match'].reset_index(drop=True)
        return result
    else:
        return pd.DataFrame()


def main():
    open(DOWNLOAD_FAILED_FILE_NAME, 'w').close()
    song_list = get_songs_to_be_downloaded()
    if len(song_list.index)>0:
        mt = MusicTools()
        logger.info('Downloading {} songs...'.format(len(song_list)))
        for index, row in song_list.iterrows():
            song_dict = mt.get_song_dict_from_title(row['full_title'])
            if song_dict:
                # pass
                logger.info(u"song_dict - title: {}".format(song_dict['title']))
                status = mt.download_music(song_dict['link'], row['full_title'], is_quiet=True)
                # status = 1
                if status == 0:
                            mt.fix_id3(row['full_title'])
                else:
                    logger.error(u"Downloading of {} failed. Moving to the next item...".format(song_dict['title']))
                    with codecs.open(DOWNLOAD_FAILED_FILE_NAME,encoding='utf-8', mode='a+') as f:
                        f.write("{}\n".format(row['full_title']))
            else:
                logger.error(u"No results found for {}. Moving to the next item...".format(row['full_title']))
                with codecs.open(DOWNLOAD_FAILED_FILE_NAME,encoding='utf-8', mode='a+') as f:
                    f.write(u"{}\n".format(row['full_title']))
        logger.info('*************************Google Music Download Finished***************************')
    else:
        logger.error("No Songs to be downloaded. Quiting...")
    logger.info(u'New Last File Read Name:{}'.format(new_end))
    with codecs.open(LAST_READ_FILE_NAME, encoding='utf-8', mode='w') as f:
        f.write('******END****\n{}'.format(new_end))

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is a script to download the thumbs up songs in Google Play Music')
    args = parser.parse_args()
    main()