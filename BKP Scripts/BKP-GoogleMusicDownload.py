
import difflib
import pandas as pd
from gmusicapi import Mobileclient
from MusicTools import MusicTools
from unidecode import unidecode
import codecs

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

APP_PASSWORD = 'ipvsapqstmkooyjt'
USER_NAME = 'manujosephv@gmail.com'
DUMP_FILE_NAME = 'D:\Music Download\GooglePlayThumbsUpExport.txt'
LAST_READ_FILE_NAME = 'D:\Music Download\last_read_line.txt'
DOWNLOAD_FAILED_FILE_NAME = 'D:\Music Download\download_failed.txt'

lib_full_title_list = []

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
	new_end = ''
	mt = MusicTools()
	with codecs.open(DUMP_FILE_NAME, encoding='utf-8') as f:
		#Skipping first line
		next(f)
	    for line in f:
	    	logger.info(line)
	    	logger.info(end in line)
	        if end in line:
	        	# logger.info('Found end')
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
			# else:
			# 	logger.error(u"Downloading of {} failed. Moving to the next item...".format(song_dict['title']))
			# 	with open(DOWNLOAD_FAILED_FILE_NAME, 'a+') as f:
			# 		f.write("{}\n".format(line))
	logger.info(u'New Last File Read Name:{}'.format(new_end))
	# with codecs.open(LAST_READ_FILE_NAME, encoding='utf-8', mode='w') as f:
	#     f.write(new_end)
	logger.debug(thumbs_up_list)
	logger.info('{} songs from Thumbs Up List'.format(len(thumbs_up_list)))
	return pd.DataFrame(thumbs_up_list)

def get_lib_from_googlemusic():
	# global USER_NAME
	# global APP_PASSWORD
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
	# logger.info('Getting all the songs in the library...')
	# lib_df = get_lib_from_googlemusic()
	# lib_df['full_title'] = lib_df['artist'] +' - '+ lib_df['title']
	# thumbs_up_df['full_title'] = thumbs_up_df['artist'] +' - '+ thumbs_up_df['title']
	# global lib_full_title_list
	# lib_full_title_list = lib_df['full_title'].values
	# logger.info('Finding out the liked songs which are not currently in the library...')
	# thumbs_up_df['matched_title'] = thumbs_up_df['full_title'].apply(closest_match)
	# result = thumbs_up_df[thumbs_up_df['matched_title'] == 'No Match']#.to_csv('no_match.csv')
	# # return result['full_title'].values
	# return result
	return 0

def closest_match(title):
    match= difflib.get_close_matches(title,lib_full_title_list, cutoff=0.7)
#     print match
    if match:
        if len(match)>0:
            return match[0]
    else:
        return "No Match"
        
def main():
	open(DOWNLOAD_FAILED_FILE_NAME, 'w').close()
	song_list = get_songs_to_be_downloaded()
	# mt = MusicTools()
	# logger.info('Downloading {} songs...'.format(len(song_list)))
	# for index, row in song_list.iterrows():
	# 	song_dict = mt.youtube_search(row['full_title'],1)[0]
	# 	score = difflib.SequenceMatcher(None,song_dict['title'].lower(),row['full_title'].lower()).ratio()
	# 	logger.info(score)
		# status = mt.download_music(song_dict['link'], row['full_title'], is_quiet=True)
		# if status == 0:
		# 			mt.fix_id3(row['full_title'])
		# else:
		# 	logger.error(u"Downloading of {} failed. Moving to the next item...".format(song_dict['title']))
		# 	with codecs.open(DOWNLOAD_FAILED_FILE_NAME,encoding='utf-8', mode='a+') as f:
		# 		f.write("{}\n".format(row['full_title']))
	# for song in song_list:
	# 	song_dict = mt.youtube_search(song,1)[0]
	# 	status = mt.download_music(song_dict['link'], song_dict['title'], is_quiet=True)
	# 	if status == 0:
	# 				mt.fix_id3(song_dict['title'])
	# 	else:
	# 		logger.error(u"Downloading of {} failed. Moving to the next item...".format(song_dict['title']))
	# 		with codecs.open(DOWNLOAD_FAILED_FILE_NAME,encoding='utf-8', mode='a+') as f:
	# 			f.write("{}\n".format(song_dict['title']))

if __name__ == '__main__':
	main()