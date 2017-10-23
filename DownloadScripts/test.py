# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 12:43:10 2017

@author: manuj
"""

import re
from gmusicapi import Mobileclient
import pandas as pd
from MusicTools import MusicTools
from pocket import Pocket, PocketException
import itertools

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
POCKET_CONSUMER_KEY = config['POCKET']['POCKET_CONSUMER_KEY']
POCKET_ACCESS_TOKEN = config['POCKET']['POCKET_ACCESS_TOKEN']

gmusic = None
youtube=None
music_tools = None

def get_gmusic_api():
    global gmusic
    if gmusic is None:
        gmusic = Mobileclient(debug_logging=False)
        gmusic.login(email=USER_NAME, password=APP_PASSWORD, locale='en_US', android_id=Mobileclient.FROM_MAC_ADDRESS)
    return gmusic

def get_music_tools():
    global music_tools
    if music_tools is None:
        music_tools= MusicTools()
    return music_tools

def get_youtube_api():
    global youtube
    if youtube is None:
        youtube = get_music_tools().get_youtube_api_object()
    return youtube
        
def get_playlist_from_channel(channel_username):
    channels_response = get_youtube_api().channels().list(
        part='contentDetails',
      forUsername=channel_username
    ).execute()
    for channel in channels_response["items"]:
        # From the API response, extract the playlist ID that identifies the list
        # of videos uploaded to the authenticated user's channel.
        return channel["contentDetails"]["relatedPlaylists"]["uploads"]

def extract_playlist_code(input_string):
    url_match = re.search(r'.*(?:youtube)\.\w+\/watch\?v=(.*)\&list=(.*)', input_string)
    if url_match:
        return url_match.group(2)
    else:
        channel_match = re.search(r'.*(?:youtube)\.\w+\/user\/(.*)',input_string)
        if channel_match:
            channel_username = channel_match.group(1)
            return get_playlist_from_channel(channel_username)
        else:
            return None

def get_song_dict(playlist_item):
    return {'test': 1}

def get_videos_from_playlist(playlist_id, full, recent_top):
    # Retrieve the list of videos uploaded to the authenticated user's channel.
    MAX_RESULTS = 50
    playlistitems_list_request = get_youtube_api().playlistItems().list(
        playlistId=playlist_id,
        part="snippet",
        maxResults=MAX_RESULTS
        )
    if recent_top<MAX_RESULTS:
        loop_outer, loop_inner = (1, recent_top)
    else:
        loop_outer, loop_inner = divmod(recent_top,MAX_RESULTS) # // operator makes sure it is a flooring division
    dict_list = []
    for i in xrange(loop_outer):
        #failsafe
        if playlistitems_list_request:
            break
        playlistitems_list_response = playlistitems_list_request.execute()
         # Loop through each video.
        for idx, playlist_item in enumerate(playlistitems_list_response["items"]):
            song_dict = get_song_dict(playlist_item)
            dict_list.append(song_dict)
            if i==loop_outer and idx == loop_inner:
                break
        playlistitems_list_request = get_youtube_api().playlistItems().list_next(playlistitems_list_request, playlistitems_list_response)
    

def main(url,full,recent_top=0):
    print 'main'
    print url
    print full
    print recent_top

def scan_pocket():
    print 'pocket'
    p = Pocket(consumer_key=POCKET_CONSUMER_KEY,access_token=POCKET_ACCESS_TOKEN)
    full = False
    logger.info('Scanning Pocket........')
    items=p.retrieve(state='unread', detailType='complete')
    for key in items['list'].keys():
        item = items['list'][key]
        url = item['given_url']
        if 'youtube' in url.lower():
            logger.info(u'Getting url for {} from Pocket'.format(item['resolved_title']))
            recent_top = 25
            for key in item:
                if key.lower().startswith('recent'):
                    recent_top = key[6:]
                if key.lower() == 'full':
                    full = True
            logger.info('url: {}, full: {}, recent: {}'.format(url,full,recent_top))
            main(url,full,recent_top)

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This is a script to port a youtube playlits to Google Music.')
    parser.add_argument('-u','--url', dest='url', type=str, help='URL of the youtube playlist/playlist code to be copied.')
    parser.add_argument('-f,','--full', dest='full', action='store_true', help='If present copies entire playlist to Google Music as a separate playlist. By default it will only copy top 25 or the value given with -t')
    parser.add_argument('-r','--recent', dest='recent', type=int, required=False, default=25, help='Copies most recent x songs from the playlist')
    parser.add_argument('-m,','--multiple', dest='multiple', action='store_true', help='To copy multiple Youtube Playlists by taking user input.')
    parser.add_argument('-p,','--pocket', dest='pocket', action='store_true', help='To copy youtube Playlists saved in Pocket.')
    args = parser.parse_args()
    if args.pocket:
        scan_pocket()
    elif args.multiple:
        input_list = []
        while True:    # infinite loop
            input_string = raw_input("Enter Youtube Playlist url/ channel user link(Exit to quit): ")
            if input_string.lower() == "exit":
                break  # stops the loop
            else:
                playlist_code = extract_playlist_code(input_string)
                while playlist_code is None:
                    input_string = raw_input("Invalid input. Youtube Playlist or Username link not detected. Please try again(Exit to quit): ")
                    playlist_code = extract_playlist_code(input_string)
                    
                full_flag = raw_input("Copy Full playlist? (Y/N): ")
                while not full_flag.lower() in ['y','n']:
                    full_flag = raw_input("Copy Full playlist? (Y/N): ")
                if full_flag.lower() == 'N':
                    full = False
                    recent_top = raw_input("No of Recent Items in separate playlist(0 will not create one): ")
                    while not recent_top.isdigit():
                        recent_top = raw_input("Invalid Input. No of Recent Items in separate playlist(0 will not create one): ")
                else:
                    full=True
                input_list.append((input_string,full,recent_top))
        for url,full,recent_top in input_list:
            main(url,full,recent_top)
    else:
        if args.url is None:
            parser.error('Without -m or -p flags, a Youtube Playlist URL or a Channel Username is required. Please use -u')
        main(extract_playlist_code(args.url),args.full,args.recent)
    logger.info('**********Port process complete***********')

