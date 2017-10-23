#!/usr/bin/python
import traceback
from apiclient.discovery import build
#from apiclient.errors import HttpError
import eyed3
from unidecode import unidecode
import re
import time
import os
import urllib2
import youtube_dl
import difflib
from bs4 import BeautifulSoup
import requests
from PyLyrics import PyLyrics
import pylast
import discogs_client
import shutil
from libpytunes import Library
import pandas as pd

# Version compatiblity
import sys
if (sys.version_info > (3, 0)):
    from urllib.request import urlopen
    from urllib.parse import quote_plus as qp
    raw_input = input
else:
    from urllib2 import urlopen
    from urllib import quote_plus as qp

import json

import logging
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MusicTools:

  # Set GOOGLE_DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
  # tab of
  #   https://cloud.google.com/console
  # Please ensure that you have enabled the YouTube Data API for your project.
  # GOOGLE_DEVELOPER_KEY = "AIzaSyC2BKr3Xm4E1Ndzg5J3O5eIXoTU-6cch0A" #My Key - Manage by going to https://console.cloud.google.com
  # YOUTUBE_API_SERVICE_NAME = "youtube"
  # YOUTUBE_API_VERSION = "v3"
  # CUSTOM_SEARCH_API_SERVICE_NAME = "customsearch"
  # CUSTOM_SEARCH_API_VERSION = "v1"
  # ALBUM_ART_SEARCH_ID = '005589030508889773928:pxhgor9bsjm'
  # DOWNLOAD_PATH ='downloaded_music'
  # LAST_FM_KEY='65a12742106c6fb80213ac344f60efc7'
  # LAST_FM_SECRET='fdd13187f923fb67ce604aed76babba0'
  # DISCOGS_KEY = 'hpNCxTnGUpwYsMuqGFgQcGzrwTFcvKyASmHcvZZb'

  last_fm_api = None
  custom_search = None
  youtube = None
  discogs_api = None

  def __init__(self):
    ### LOADING THE CONFIG VARIABLES FROM FILE
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except:
        with open('../config.json', 'r') as f:
            config = json.load(f)

      # Set GOOGLE_DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
      # tab of
      #   https://cloud.google.com/console
      # Please ensure that you have enabled the YouTube Data API for your project.
    self.GOOGLE_DEVELOPER_KEY = config['MUSICTOOLS']['GOOGLE_DEVELOPER_KEY'] #My Key - Manage by going to https://console.cloud.google.com
    self.YOUTUBE_API_SERVICE_NAME = config['MUSICTOOLS']['YOUTUBE_API_SERVICE_NAME']
    self.YOUTUBE_API_VERSION = config['MUSICTOOLS']['YOUTUBE_API_VERSION']
    self.CUSTOM_SEARCH_API_SERVICE_NAME = config['MUSICTOOLS']['CUSTOM_SEARCH_API_SERVICE_NAME']
    self.CUSTOM_SEARCH_API_VERSION = config['MUSICTOOLS']['CUSTOM_SEARCH_API_VERSION']
    self.ALBUM_ART_SEARCH_ID = config['MUSICTOOLS']['ALBUM_ART_SEARCH_ID']
    self.DOWNLOAD_PATH = config['MUSICTOOLS']['DOWNLOAD_PATH']
    self.LAST_FM_KEY = config['MUSICTOOLS']['LAST_FM_KEY']
    self.LAST_FM_SECRET = config['MUSICTOOLS']['LAST_FM_SECRET']
    self.DISCOGS_KEY = config['MUSICTOOLS']['DISCOGS_KEY']


  def get_discogs_api_object(self):
    if self.discogs_api:
      return self.discogs_api
    else:
      self.discogs_api = discogs_client.Client('ExampleApplication/0.1', user_token=self.DISCOGS_KEY)
      return self.discogs_api

  def get_youtube_api_object(self):
    if self.youtube:
      return self.youtube
    else:
      self.youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
      developerKey=self.GOOGLE_DEVELOPER_KEY, cache_discovery=False)
      return self.youtube

  def get_custom_search_api_object(self):
    if self.custom_search:
      return self.custom_search
    else:
      self.custom_search = build(self.CUSTOM_SEARCH_API_SERVICE_NAME, self.CUSTOM_SEARCH_API_VERSION,
               developerKey=self.GOOGLE_DEVELOPER_KEY, cache_discovery=False)
      return self.custom_search
  
  def get_last_fm_api_object(self):
    if self.last_fm_api:
      return self.last_fm_api
    else:
      self.last_fm_api = pylast.LastFMNetwork(api_key=self.LAST_FM_KEY, api_secret=self.LAST_FM_SECRET)
      return self.last_fm_api

  def get_genre_from_last_fm(self,mp3):
    network = self.get_last_fm_api_object()
    genre = 'Unavailable'
    if mp3.tag:
        try:
            artist = network.get_artist(mp3.tag.artist)
            if artist:
                top_itms = artist.get_top_tags()
                if top_itms:
                    if len(top_itms)>0:
                        top_itm = top_itms[0]
                        tag = top_itm.item
                        if tag:
                            genre = tag.get_name()
        except pylast.WSError:
            logger.debug("Genre not found for {}".format(mp3.tag.title))
        #Need to log the error
    return genre

  def get_album_art_discogs(self,artist,title):
    d = self.get_discogs_api_object()
    results = d.search(release_title=title,artist=artist,type='release')
    if len(results)>0:
        release = results[0]
        images = release.images
        if len(images)>0:
            return images[0]['resource_url']
    return None


  def get_album_art_google(self,query):
    # To skip Google Search while testing.
    # print (1/0)
    custom_search = self.get_custom_search_api_object()
    search_response= custom_search.cse().list(
    q=query,
    cx=self.ALBUM_ART_SEARCH_ID,
    searchType='image',
    imgType = 'photo',
    num=10,
    safe= 'off'
    ).execute()
    for item in search_response['items']:
      if item['image']['height'] == item['image']['width']:
        return item['link']
    return search_response['items'][0]['link']

  def get_album_art_last_fm(self,artist, title):
    network = self.get_last_fm_api_object()
    album = network.get_track(artist, title).get_album()
    if album:
        return album.get_cover_image(size=4)
    else:
        return None


  def get_album_art(self,artist, title):
    try:
      link = self.get_album_art_last_fm(artist, title)
      if link:
        return link
    except Exception as e:
      logger.debug(e)
      # traceback.print_exc()
      pass
    logger.debug("Error in getting AlbumArt from Last.FM. Trying Discogs")
    
    try:
      link = self.get_album_art_discogs(artist, title)
      if link:
        return link
    except Exception as e:
      logger.debug(e)
      # traceback.print_exc()
      pass
    logger.debug("Error in getting AlbumArt from Discogs. Trying Google")
    
    try:
      link = self.get_album_art_google(artist +' - ' + title)
      if link:
        return link
    except Exception as e:
      logger.debug(e)
      traceback.print_exc()
      pass
    logger.debug("Error in getting AlbumArt from Google. Skipping..")
    
    return None

#  def get_album_art(self,artist, title):
#    try:
#      link = self.get_album_art_google(artist +' - ' + title)
#      if link:
#        return link
#    except Exception as e:
#      pass
#      logger.debug("Error in getting AlbumArt from Google. Trying Last.FM")
#      logger.debug(e)
#      try:
#        link = self.get_album_art_last_fm(artist, title)
#        logger.debug(link)
#        if link:
#          return link
#      except IOError as e:
#        pass
#      logger.debug("Error in getting AlbumArt from Last.FM. Skipping")
#      logger.debug(e)
#      return None



  def youtube_search(self,query,max_results):

    youtube = self.get_youtube_api_object()
    #To get the audio and not the video
    query = query + ' audio'

    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
      q=query,
      part="id,snippet",
      maxResults=max_results
    ).execute()

    videos = []
    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
      if search_result["id"]["kind"] == "youtube#video":
        video_dict = {}
        video_dict['title'] = search_result["snippet"]["title"]
        video_dict['link'] = "http://www.youtube.com/watch?v={}".format(search_result["id"]["videoId"])
        videos.append(video_dict)
    return videos

  def get_title_youtube(self,vid):
    youtube = self.get_youtube_api_object()

    # Call the videos.list method to retrieve results matching the specified
    # video code.
    search_response = youtube.videos().list(
    part='snippet',
        id=vid,
    ).execute()
    return search_response['items'][0]['snippet']['title']

  def request_website(self,url, max_attempts):
    attempts = 0
    while attempts < max_attempts+1:
        try :
            req = urllib2.Request(url, headers={'User-Agent' : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30"}) 
            # print('Opening Page') #ADd timeout
            web_page = urllib2.urlopen(req, timeout=30)
            return web_page
            # print('Opened Page') #ADd timeout
            break
        except urllib2.HTTPError:
                print("HTTP ERROR!")
                # print(err.code)
                attempts += 1
                print("Retrying...")
                time.sleep(5)
                if attempts == max_attempts:
                    return None
        except urllib2.URLError :
            print("URL ERROR!")
            attempts += 1
            print("Retrying...")
            time.sleep(5)
            if attempts == max_attempts:
                return None
        except Exception, e:
            print("An ERROR! {}".format(str(e)))
            attempts += 1
            print("Retrying...")
            time.sleep(5)
            if attempts == max_attempts:
                return None


  def search_soundcloud(self,query, max_results):
    url = "https://soundcloud.com/search/sounds?q={}".format(query.replace(" ", "%20"))
    web_page = self.request_website(url,3)
    if web_page:
      soup = BeautifulSoup(web_page,'html.parser')
      search_list = soup.findAll('li')
      result_counter = 0
      results = []
      for li in search_list:
    #         print(li.get_text())
          everything = 'Everything' in li.get_text()
          tracks = 'Tracks' in li.get_text()
          playlists = 'Playlists' in li.get_text()
          people = 'People' in li.get_text()
          flag = not(everything|tracks|playlists|people)
          if flag:
              video_dict = {}
              result_counter = result_counter+1
              a_tag = li.find_next('a')
              video_dict['link'] ="www.soundcloud.com{}".format(a_tag['href'])
              video_dict['title'] = a_tag.get_text()
    #             print title
              results.append(video_dict)
              if result_counter >= max_results:
                  break
      return results
    else:
      return "No Connection Made"

  def get_title_soundcloud(self,url):
    web_page = self.request_website(url,3)
    if web_page:
      soup = BeautifulSoup(web_page,'html.parser')
      return soup.find('meta',{'property':'og:title'})['content']
    else:
      return "No connection made"

  def get_clean_title(self,title):
    #Removing | from title if any
    if "|" in title:
      title = title.replace('|','')

    words_filter = ('official', 'lyric video', 'official video','official music video','lyrics','official lyric video','official lyrics video','lyric', 'audio', 'remixed', 'video',
            'full', 'version', 'music', 'mp3', 'hd', 'hq', 'uploaded', 'reupload','re-upload','proximity release','edm.com exclusive','edm.com premeire'
            ,'free download!','free download')
    word_filter_calc = ["("+word+")" for word in words_filter] + ["["+word+"]" for word in words_filter] + ["{"+word+"}" for word in words_filter] 
    match = re.search(r'(.*)((\(|\[|\{).*(\)|\]|\}))',title)
    if match:
        song_name_words = match.group(1).split()+[match.group(2)]
#         print("regex match found")
    else:
        song_name_words = title.split()
#         print('normal split:{}'.format(len(song_name_words)))
    result_words = [word for word in song_name_words if word.lower() not in word_filter_calc]
    result = ' '.join(result_words)
    # result.decode('unicode_escape').encode('ascii','ignore')
    return unidecode(result)

  def get_youtube_link_from_item(self,item):
    match = re.search(r'((https|http)://\w+.youtube.\w+/watch\?v=.+)\s\((.+)\)', item)
    if match:
        return match.group(1)
    else:
        match = re.search(r'((https|http)://youtu\.be/\w+)\s\((.+)\)', item) 
        if match:
          return match.group(1)
        else: 
          return None

  def get_soundcloud_link_from_item(self,item):
      match = re.search(r'((https|http)://soundcloud.\S+)', item)
      if match:
          return match.group(1)
      else:
          return None
  def get_youtube_code_from_link(self,link):
      tag = re.search(r'(https|http)://\w+.youtube.\w+/watch\?v=(.{11})', link)
      if tag:
          return tag.group(2)
      else:
          tag = re.search(r'(https|http)://youtu\.be/(.{11})', link)
          if tag:
            return tag.group(2)
          else:
            return None

  def get_youtube_link(self,title):
       #Searching in Youtube
      search_results = self.youtube_search(title,1)
      if len(search_results)>0:
          song_dict = search_results[0]
          score = difflib.SequenceMatcher(None,song_dict['title'].lower(),title.lower()).ratio()
          if score < 0.50:
              logger.warning(u"Youtube Title: {}, Actual Title: {}, Score: {}. No satisfactory results in Youtube".format(song_dict['title'],title,score))
              return None
      else:
          logger.warning(u"No Results for {} in Youtube".format(title))
          return None
      return song_dict

  def get_soundcloud_link(self,title):
      #Searching in Soundcloud
      try:
          search_results = self.search_soundcloud(title,1)
          if len(search_results)>0:
              song_dict = search_results[0]
              score = difflib.SequenceMatcher(None,song_dict['title'].lower(),title.lower()).ratio()
              if score <0.5:
                  logger.warning(u"Soundcloud Title: {}, Actual Title: {}, Score: {}. No satisfactory results in Soundcloud".format(song_dict['title'],title,score))
                  return None
          else:
              logger.warning(u"No Results found in Soundcloud also for {}. Skipping..".format(title))
              return None
      except Exception:
          logger.warning(u"No Results found in Soundcloud also for {}. Skipping..".format(title))
          return None
      return song_dict


  def get_song_dict_from_title(self,title):
      song_dict = self.get_youtube_link(title)
      if not(song_dict):
          song_dict = self.get_soundcloud_link(title)
      return song_dict



  def download_music(self, video_link, title, is_quiet=False):
    # logger.info('Disabled download for testing')
    # return 1
    if "youtube" in video_link:
      download_source = 'YouTube'
    elif "soundcloud" in video_link:
      download_source = "Soundcloud"
    logger.info(u'Downloading {} from {}...'.format(title, download_source))
    ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
          }],
    'outtmpl': u'/'+ self.DOWNLOAD_PATH +'/'+title+'.%(ext)s' ,
    # 'outtmpl': u''+ os.path.join(config['DEFAULT']['ROOT'],config['MUSICTOOLS']['DOWNLOAD_PATH'],title+'.%(ext)s') ,
    'quiet':is_quiet,
    # 'outtmpl': '/music/%(title)s.%(ext)s' ,
      }
    try:  
      with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        r = ydl.download([video_link])
    except Exception: #youtube_dl.utils.DownloadError
      r = 1
      # logger.error(e.message+" Moving on to the next item...")
    #1 is a failure, 0 is a success
    return r

  def fix_id3(self,title):
    logger.debug(u'Writing ID3 tags to {}...'.format(title))
    try:
        # audiofile = eyed3.load(self.DOWNLOAD_PATH+title+'.mp3')
        full_path = os.path.join(os.getcwd(), self.DOWNLOAD_PATH, title+'.mp3')
        logger.debug(u'MP3 file path for loading is: {}'.format(full_path))
        if os.path.exists(full_path):
          try:
            audiofile = eyed3.load(full_path)
          except UnicodeEncodeError:
            files = os.listdir(os.path.join(os.getcwd(), self.DOWNLOAD_PATH))
            closest_file = difflib.get_close_matches(title+'.mp3',files)[0]
            full_path = os.path.join(os.getcwd(), self.DOWNLOAD_PATH, closest_file)
            audiofile = eyed3.load(full_path)
        else:
          files = os.listdir(os.path.join(os.getcwd(), self.DOWNLOAD_PATH))
          closest_file = difflib.get_close_matches(title+'.mp3',files)[0]
          full_path = os.path.join(os.getcwd(), self.DOWNLOAD_PATH, closest_file)
          audiofile = eyed3.load(full_path)
        if audiofile.tag is None:
          audiofile.tag = eyed3.id3.Tag()
          # audiofile.tag.file_info = eyed3.id3.FileInfo("foo.id3")
        logger.debug(u'Title to be split:{}'.format(title))
        list_name = title.split('-')
        try:
            artist=list_name[0]
            track_name = list_name[1]
        except IndexError:
            logger.warning("Title not in desired format. Writing Title to both artist and title")
            artist = title
            track_name = title
        album_name = ""
        try:
          logger.debug(u'Getting Lyrics for {} from LyricsWikia'.format(title))
          lyrics = PyLyrics.getLyrics(artist,track_name)
          audiofile.tag.lyrics.set(u''+lyrics)
        except ValueError as e:
            logger.warning(e.message)                 
        
        logger.debug(u"Writing these to tags: artist:{}, Track name: {}, Album Name: {}".format(artist,track_name,album_name))
        artist=artist.strip()
        track_name=track_name.strip()
        album_name=album_name.strip()
        # print (artist,track_name,album_name)

        audiofile.tag.artist=unicode(artist)
        audiofile.tag.album_artist=unicode(artist)
        audiofile.tag.title=unicode(track_name)
        audiofile.tag.album =unicode(album_name)

        genre = self.get_genre_from_last_fm(audiofile)
        if genre:
          audiofile.tag.genre =unicode(genre)
        else:
          logger.warning('Genre not found for {}'.format(title))
        try:
            logger.debug("Getting AlbumArt from Google...")
            image_link = self.get_album_art(artist, track_name)
            imagedata = requests.get(image_link).content
            audiofile.tag.images.set(0,imagedata,"image/jpeg",u"Album Art")
        except Exception as e:
            logger.error("Error in getting AlbumArt. Won't be saved to Tag")
            logger.debug(e)
        
        audiofile.tag.save()
        logger.info(u'ID3 Tags written and saved to {}...'.format(title))

    except IOError:
        logger.error(u"Can't open file. ID3 tags skipped:{}".format(title))
    except Exception as e:
        logger.exception("Something awful has happened")
        logger.debug(e)


##### Not part of the class
### LOADING THE CONFIG VARIABLES FROM FILE
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except:
    with open('../config.json', 'r') as f:
        config = json.load(f)

ITUNES_PATH = config['MUSICTOOLS']['ITUNES_PATH']
BACKUP_PATH = config['DEFAULT']['ROOT']
# ITUNES_PATH = "D:\Music\iTunes\iTunes Library.xml"
# BACKUP_PATH = 'D:\Music Download'

def closest_match(title,lib_full_title_list):
  match= difflib.get_close_matches(title,lib_full_title_list, cutoff=0.8)
  #     print match
  if match:
      if len(match)>0:
          return match[0]
  else:
      return "No Match"


def strip_ft(artist):
    l = re.compile("\s\(?(ft(.)?|feat(.)?|featuring(.)?)\s").split(unicode(artist).lower())
    if len(l)>0:
        return l[0]
    else:
        return artist

def get_stripped_title(self,title):
    split = re.split(r'(?: ?)-(?: ?)',title)
    if len(split)>1:
        artist = re.split(r'(?: *?)(?:\(|\[|\{)?(ft\.?|feat\.?|featuring\.?)',split[0])[0]
        match_remix = re.search(r'(.*)(?: *?)(?:\(|\[|\{)?(ft\.?|feat\.?|featuring\.?)(.*)(\(.*\))',split[1])
        if match_remix:
            title_without_ft = match_remix.group(1)+match_remix.group(4)
        else:
            match_ft = re.search(r'(.*)(?: +?)(?:\(|\[|\{)?(ft\.?|feat\.?|featuring\.?)(?: +?)(.*)(?:\)|\]|\})?',split[1])
            if match_ft:
                title_without_ft = match_ft.group(1)
            else:
                title_without_ft = split[1]
        return artist + ' - ' + title_without_ft
    else:
        return title

def backup_file(file_path, backup_path):
    logger.info('Copying iTunes xml to working directory')
    path, file_name = os.path.split(file_path)
    backup_full_path = os.path.join(backup_path,file_name)
    #Copy
    shutil.copy(file_path,backup_full_path)
    return backup_full_path

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