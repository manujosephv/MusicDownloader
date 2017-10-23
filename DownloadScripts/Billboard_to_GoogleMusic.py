import billboard
import pandas as pd
import datetime as dt
from gmusicapi import Mobileclient


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

APP_PASSWORD = config['GOOGLEMUSIC']['APP_PASSWORD']
USER_NAME = config['GOOGLEMUSIC']['USER_NAME']

charts_to_playlist = [('HOT_100',"Billboard Hot 100 Chart"),('TOP_HIPHOP', 'Billboard R&B and HipHop Chart'),('TOP_EDM', 'Billboard EDM Chart')] #
#gmusic = Mobileclient(debug_logging=False)
#logged_in = gmusic.login(email=USER_NAME, password=APP_PASSWORD, locale='en_US', android_id=Mobileclient.FROM_MAC_ADDRESS)
gmusic = None

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
        song_dict['change'] = entry.change
        try:
            first_result = gmusic.search(song_dict['full_title_stripped'])['song_hits'][0]['track']
        except Exception as e:
            logger.debug('Exception: {}'.format(e))
            logger.info(u'Skipped {}'.format(song_dict['full_title']))
#         song_dict['date'] = current_week(dt.datetime.today())
        song_dict['song_id']=first_result['storeId']
        if first_result.has_key('rating'):
            song_dict['rating']=first_result['rating']
        else:
            song_dict['rating'] = 0
        dict_list.append(song_dict)
    return pd.DataFrame(dict_list)

def current_week(day):
    day_of_week = day.weekday()

    to_beginning_of_week = dt.timedelta(days=day_of_week)
    beginning_of_week = day - to_beginning_of_week

    return beginning_of_week.strftime('%d-%b-%y')

def delete_playlist_if_exists(name):
    all_playlists=gmusic.get_all_playlists()
    for playlist in all_playlists:
        if playlist['name'] == name:
            gmusic.delete_playlist(playlist['id'])

def main():
    logger.info('Scanning the Billboard Charts......')
    chart_df_dict = {}
    global gmusic
    if not gmusic:
        gmusic = Mobileclient(debug_logging=False)
        gmusic.login(email=USER_NAME, password=APP_PASSWORD, locale='en_US', android_id=Mobileclient.FROM_MAC_ADDRESS)
    for chart,chart_name in charts_to_playlist:
        logger.info('Getting {}......'.format(chart_name))
        chart_scraped = billboard.ChartData(config['BILLBOARD'][chart])
        chart_df = get_song_df(chart_scraped)
        #Delete Playlist if present.
        logger.info('Updating {} Playlist......'.format(chart_name))
        delete_playlist_if_exists(chart_name)
        #Create Playlist
        playlist_id=gmusic.create_playlist(name=chart_name, description=chart_name+' from Billboard on week {}'.format(current_week(dt.datetime.today())), public=True)
        gmusic.add_songs_to_playlist(playlist_id=playlist_id, song_ids=chart_df.song_id.dropna().tolist())
        chart_df_dict[chart] = chart_df
	#Top Rising from Hot 100
	if chart_df_dict.has_key('HOT_100'):
	    logger.info('Updating {} Playlist......'.format('Top 25 Risers'))
	    top_100=chart_df_dict['HOT_100']
	    top_100.loc[top_100.change=='Hot Shot Debut','change'] = 100
	    top_100.change = pd.to_numeric(top_100.change, errors='coerce').fillna(0)
	    hot25_risers=top_100.sort_values(by=['change'], ascending=False).head(25).sort_values(by=['rank'], ascending=True)
	    delete_playlist_if_exists('Top 25 Risers')
	    playlist_id=gmusic.create_playlist('Top 25 Risers', 'Top 25 Risers from Hot 100 Billboard on week {}'.format(current_week(dt.datetime.today())))
	    gmusic.add_songs_to_playlist(playlist_id=playlist_id, song_ids=hot25_risers.song_id.dropna().tolist())
	    logger.info('Finished Updating......'.format('Top 25 Risers'))

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is a script to update the playlists in Google Music with latest Billboard Charts')
    args = parser.parse_args()
    main()
        


