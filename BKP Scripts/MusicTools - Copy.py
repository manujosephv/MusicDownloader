#!/usr/bin/python

from apiclient.discovery import build
from apiclient.errors import HttpError
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
from PyLyrics import *
# Version compatiblity
import sys
if (sys.version_info > (3, 0)):
    from urllib.request import urlopen
    from urllib.parse import quote_plus as qp
    raw_input = input
else:
    from urllib2 import urlopen
    from urllib import quote_plus as qp


import logging
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class MusicTools:

  # Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
  # tab of
  #   https://cloud.google.com/console
  # Please ensure that you have enabled the YouTube Data API for your project.
  DEVELOPER_KEY = "AIzaSyC2BKr3Xm4E1Ndzg5J3O5eIXoTU-6cch0A" #My Key - Manage by going to https://console.cloud.google.com
  YOUTUBE_API_SERVICE_NAME = "youtube"
  YOUTUBE_API_VERSION = "v3"
  CUSTOM_SEARCH_API_SERVICE_NAME = "customsearch"
  CUSTOM_SEARCH_API_VERSION = "v1"
  ALBUM_ART_SEARCH_ID = '005589030508889773928:pxhgor9bsjm'
  DOWNLOAD_PATH ='downloaded_music'

  def get_album_art(self,query):
    custom_search = build(self.CUSTOM_SEARCH_API_SERVICE_NAME, self.CUSTOM_SEARCH_API_VERSION,
               developerKey=self.DEVELOPER_KEY, cache_discovery=False)
    search_response= custom_search.cse().list(
    q=query,
    cx=self.ALBUM_ART_SEARCH_ID,
    searchType='image',
    imgType = 'photo',
    num=1,
    safe= 'off'
    ).execute()
    return search_response['items'][0]['link']


  def youtube_search(self,query,max_results):

    youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
      developerKey=self.DEVELOPER_KEY, cache_discovery=False)

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
    youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
    developerKey=self.DEVELOPER_KEY, cache_discovery=False)

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
            'full', 'version', 'music', 'mp3', 'hd', 'hq', 'uploaded', 'reupload','re-upload')
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
          return None

  def download_music(self, video_link, title, is_quiet=False):
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
    'quiet':is_quiet,
    # 'outtmpl': '/music/%(title)s.%(ext)s' ,
      }
    try:  
      with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        r = ydl.download([video_link])
    except Exception  as e: #youtube_dl.utils.DownloadError
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

        try:
            logger.debug("Getting AlbumArt from Google...")
            image_link = self.get_album_art(title)
            imagedata = requests.get(image_link).content
            audiofile.tag.images.set(0,imagedata,"image/jpeg",u"Album Art")
        except Exception as e:
            logger.error("Error in getting AlbumArt. Won't be saved to Tag")
        
        audiofile.tag.save()
        logger.info(u'ID3 Tags written and saved to {}...'.format(title))

    except IOError:
        logger.error(u"Can't open file. ID3 tags skipped:{}".format(title))
    except Exception as e:
        logger.exception("Something awful has happened")