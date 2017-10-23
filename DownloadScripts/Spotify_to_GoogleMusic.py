import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from gmusicapi import Mobileclient
import pandas as pd
import HTMLParser
from pocket import Pocket, PocketException

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
SPOTIPY_CLIENT_ID = config['SPOTIFY']['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET = config['SPOTIFY']['SPOTIPY_CLIENT_SECRET']
POCKET_CONSUMER_KEY = config['POCKET']['POCKET_CONSUMER_KEY']
POCKET_ACCESS_TOKEN = config['POCKET']['POCKET_ACCESS_TOKEN']


sp = None
gmusic = None
logged_in = None
html_parser = None


def get_song_df(tracks):
    dict_list = []
    for tracks in tracks['items']:
        song_dict = {}
        track = tracks['track']
        song_dict['artist'] = html_parser.unescape(track['artists'][0]['name'])
        song_dict['title'] = html_parser.unescape(track['name'])
        song_dict['full_title'] = song_dict['artist'] + ' - ' + song_dict['title'].split(' - ')[0]
        song_dict['popularity'] = track['popularity']
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


def delete_playlist_if_exists(name):
    all_playlists=gmusic.get_all_playlists()
    for playlist in all_playlists:
        if playlist['name'] == name:
            gmusic.delete_playlist(playlist['id'])


def port_playlist_google_music(playlist_url, sort_popularity):
    match = re.search(r'(https|http)://.+/user/(.+)/playlist/(.+)',playlist_url)
    if match:
        username = match.group(2)
        playlist_id = match.group(3)
        logger.debug(u'username: {}, playlist id: {}'.format(username, playlist_id))
        results = sp.user_playlist(username, playlist_id, fields="name,description,tracks,next")
        playlist_name = html_parser.unescape(results['name'])
        if results.has_key('description') and results['description'] is not None:
            playlist_desc = html_parser.unescape(results['description'])
        else:
            playlist_desc = playlist_name
        logger.info(u'Copying {} from Spotify to Google Music'.format(playlist_name))
        logger.debug(u'Playlist Name: {}, Playlist Description: {}'.format(playlist_name, playlist_desc))
        tracks = results['tracks']
        logger.info('Scanning page 1')
        i=2
        song_df=get_song_df(tracks)
        while tracks['next']:
            tracks = sp.next(tracks)
            logger.info('Scanning page {}'.format(i))
            i=i+1
            song_df = song_df.append(get_song_df(tracks), ignore_index=True)
        if sort_popularity:
            song_df.sort_values('popularity', ascending = False, inplace=True)
        #Delete Playlist if present.
        delete_playlist_if_exists(playlist_name)
        #Create Playlist
        playlist_id=gmusic.create_playlist(name=playlist_name, description=playlist_desc, public=True)
        gmusic.add_songs_to_playlist(playlist_id=playlist_id, song_ids=song_df.song_id.dropna().tolist())
        logger.info(u'{} successfully copied'.format(playlist_name))
    else:
        logger.info('Invalid URL. Should be in the format: https://open.spotify.com/user/<username>/playlist/<playlist id>. Given {}'.format(playlist_url))

def main(playlist_url, sort_popularity):
    global sp
    global gmusic
    global html_parser
    if not sp:
        client_credentials_manager = SpotifyClientCredentials(client_id='3f287f09db8e4980ac4fe8b6082886f6', client_secret='0bb44d1efcfd497380c2148a7f1b9cb3')
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    if not gmusic:
        gmusic = Mobileclient(debug_logging=False)
        logged_in = gmusic.login(email=USER_NAME, password=APP_PASSWORD, locale='en_US', android_id=Mobileclient.FROM_MAC_ADDRESS)
    if not html_parser:
        html_parser = HTMLParser.HTMLParser()
    port_playlist_google_music(playlist_url, sort_popularity)

def scan_pocket():
    p = Pocket(consumer_key=POCKET_CONSUMER_KEY,access_token=POCKET_ACCESS_TOKEN)
    logger.info('Scanning Pocket........')
    items=p.retrieve(state='unread', detailType='complete')
    for key in items['list'].keys():
        item = items['list'][key]
        url = item['given_url']
        if 'spotify' in url.lower():
            logger.info(u'Getting url for {} from Pocket'.format(item['resolved_title']))
            flag = False
            if item.has_key('tags'):
                if item['tags'].has_key('sort'):
                    flag = True
            logger.info('url: {}, flag: {}'.format(url,flag))
            main(url,flag)
        # p.archive(key)
    # p.commit()



import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This is a script to port a spotify playlist to Google Music.')
    parser.add_argument('-u','--url', dest='url', type=str, help='URL of the Spotify playlist to be copied.')
    parser.add_argument('-s','--sort', dest='sort', action='store_true', help='To sort in the order of the popularity of the track in Spotify.')
    parser.add_argument('-m,','--multiple', dest='multiple', action='store_true', help='To copy multiple Spotify Playlists by taking user input.')
    parser.add_argument('-p,','--pocket', dest='pocket', action='store_true', help='To copy Spotify Playlists saved in Pocket.')
    args = parser.parse_args()
    if args.pocket:
        scan_pocket()
    elif args.multiple:
        input_list = []
        while True:    # infinite loop
            input_string = raw_input("Enter Spotify Playlist url(Exit to quit): ")
            if input_string.lower() == "exit":
                break  # stops the loop
            else:
                popularity_sort_flag = raw_input("Sort by Popularity? (Y/N): ")
                while popularity_sort_flag.lower() not in ['y','n']:
                    popularity_sort_flag = raw_input("Invalid Input. Sort by Popularity? (Y/N): ")
                if popularity_sort_flag.lower() == 'Y':
                    sort_flag = True
                else:
                    sort_flag = False
                input_list.append((input_string,sort_flag))
        for url, flag in input_list:
            main(url,flag)
    else:
        if args.url is None:
            parser.error('Without -m or -p flags, a Spotify Playlist URL is required. Please use -u')
        main(args.url,args.sort)
    logger.info('**********Port process complete***********')

