import billboard
import pandas as pd
import os
import datetime as dt
from MusicTools import MusicTools
from MusicTools import closest_match, get_itunes_lib
#from unidecode import unidecode
import codecs

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#import configparser
import json
### LOADING THE CONFIG VARIABLES FROM FILE
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except:
    with open('../config.json', 'r') as f:
        config = json.load(f)

HOT_100 = config['BILLBOARD']['HOT_100']
TOP_HIPHOP = config['BILLBOARD']['TOP_HIPHOP']
TOP_EDM = config['BILLBOARD']['TOP_EDM']
DOWNLOAD_FAILED_FILE_NAME = os.path.join(config['DEFAULT']['ROOT'],config['BILLBOARD']['DOWNLOAD_FAILED_FILE_NAME']) 
LAST_DOWNLOAD = os.path.join(config['DEFAULT']['ROOT'],config['BILLBOARD']['LAST_DOWNLOAD']) 
MAX_SONG_DOWNLOAD = config['BILLBOARD']['MAX_SONGS']


def get_song_df(chart_list):
    dict_list = []
    for entry in chart_list:
        song_dict = {}
        song_dict['artist'] = entry.artist
        if 'Featuring' in entry.artist:
            parts = entry.artist.split(' Featuring ')
            song_dict['artist_stripped'] = parts[0]
        else:
            song_dict['artist_stripped'] = entry.artist
        song_dict['title'] = entry.title
        song_dict['full_title'] = entry.artist + ' - ' + entry.title
        song_dict['full_title_stripped'] = song_dict['artist_stripped']  + ' - ' + entry.title
        song_dict['rank'] = entry.rank
        song_dict['date'] = dt.datetime.now()
        dict_list.append(song_dict)
    return pd.DataFrame(dict_list)

def get_billboard_chart():
    hot_100 = billboard.ChartData(HOT_100)
    top_hiphop = billboard.ChartData(TOP_HIPHOP)
    top_edm = billboard.ChartData(TOP_EDM)
    #Getting the charts
    top_100_df = get_song_df(hot_100.entries)
    top_edm_df = get_song_df(top_edm.entries)
    top_hiphop_df = get_song_df(top_hiphop)
    #Removing Duplicates and concatenating the dfs
    edm_title_list = top_edm_df.full_title.get_values()
    top_100_title_list = top_100_df.full_title.get_values()
    mask_edm = [entry not in top_100_title_list for entry in edm_title_list]
    top_edm_df = top_edm_df[mask_edm]
    hiphop_title_list = top_hiphop_df.full_title.get_values()
    mask_hiphop = [entry not in top_100_title_list for entry in hiphop_title_list]
    top_hiphop_df = top_hiphop_df[mask_hiphop]
    hiphop_title_list_new = top_hiphop_df.full_title.get_values()
    edm_title_list_new = top_edm_df.full_title.get_values()
    mask_edm_hiphop = [entry not in edm_title_list_new for entry in hiphop_title_list_new]
    top_hiphop_df = top_hiphop_df[mask_edm_hiphop]
    concat_billboard_charts = pd.concat([top_100_df,top_edm_df,top_hiphop_df]).sort_values(by='rank')
    return concat_billboard_charts

def get_chart_songs_to_download():
    logger.info('Getting charts from Billboard')
    billboard_chart_df = get_billboard_chart()
    logger.debug('Billboard chart length: {}'.format(len(billboard_chart_df.index)))
    logger.info('Checking for new songs from last download'.format(len(billboard_chart_df.index)))
    last_download_chart = pd.read_pickle(LAST_DOWNLOAD)
    billboard_chart_df.to_pickle(LAST_DOWNLOAD)
    billboard_chart_df['old_matched_title'] = billboard_chart_df['full_title_stripped'].apply(lambda x: closest_match(x,last_download_chart.full_title_stripped.values))
    billboard_chart_df = billboard_chart_df[billboard_chart_df['old_matched_title']=='No Match'].reset_index(drop=True)
    logger.info('Getting songs from iTunes library')
    itunes_lib = get_itunes_lib()
    logger.debug('Itunes Lib length: {}'.format(len(itunes_lib.index)))
    logger.info('Finding out songs which are already in the library')
    billboard_chart_df['matched_title'] = billboard_chart_df['full_title_stripped'].apply(lambda x: closest_match(x,itunes_lib.full_title_stripped.values))
    songs_not_in_lib = billboard_chart_df[billboard_chart_df['matched_title']=='No Match'].reset_index(drop=True)
    logger.debug('songs not in lib length: {}'.format(len(songs_not_in_lib.index)))
    global MAX_SONG_DOWNLOAD
    if MAX_SONG_DOWNLOAD < len(songs_not_in_lib.index):
        MAX_SONG_DOWNLOAD = len(songs_not_in_lib.index)+1
    return songs_not_in_lib.loc[:MAX_SONG_DOWNLOAD-1,:]

def main(max_song_download=MAX_SONG_DOWNLOAD):
    # global MAX_SONG_DOWNLOAD
    # MAX_SONG_DOWNLOAD = max_song_download
    open(DOWNLOAD_FAILED_FILE_NAME, 'w').close()
    song_list = get_chart_songs_to_download()
    if len(song_list.index)>0:
        mt = MusicTools()
        logger.info('Downloading {} songs...'.format(len(song_list)))
        for index, row in song_list.iterrows():
            song_dict = mt.get_song_dict_from_title(row['full_title'])
            if song_dict:
                # pass
                logger.info(u"song_dict - title: {}".format(song_dict['title']))
                status = mt.download_music(song_dict['link'], row['full_title'], is_quiet=True)
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
        logger.info('*************************Billboard Chart Download Finished***************************')
    else:
        logger.error("No Songs to be downloaded. Quiting...")


import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This is a script to download the top songs from the Billboard Charts')
    parser.add_argument('-l','--limit', type=int,help='This specified the top x number of songs to be downloaded. If left blank, top 25 songs are downloaded.', required=False, default = 25)
    args = parser.parse_args()
    main(args.limit)