
import os
import shutil
import eyed3
from MusicTools import MusicTools
import logging
import requests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
import argparse
__author__ = 'Manu Joseph'

SOURCE_FOLDER = 'D:\Music Download\DownloadScripts\No Albumart'
DESTINATION_FOLDER = 'D:\Music Download\DownloadScripts\Found Albumart'

def main(source_folder, destination_folder):
	dict_list = {}
	# folder = 'D:\Music Download\No Albumart'
	mt = MusicTools()
	for root, dirs, files in os.walk(source_folder):
	    for name in files:
	        dict_file = {}
	        if name.endswith((".mp3")):
	            logger.info(name)
	            mp3 = eyed3.load(os.path.realpath(os.path.join(root,name)))
	            # print ("File: {}".format(name))
	            if mp3.tag:
	                if len( mp3.tag.images ) != 0:
	                    # print ("No AlbumArt")
	                    logger.info('AlbumArt already present...moving the file to completion...')
	                    shutil.move(os.path.realpath(os.path.join(root,name)), os.path.realpath(os.path.join(destination_folder,name)))
	                else:
	                    try:
	                        image_link = mt.get_album_art(mp3.tag.artist, mp3.tag.title)
	                        imagedata = requests.get(image_link).content
	                        mp3.tag.images.set(0,imagedata,"image/jpeg",u"Album Art")
	                        mp3.tag.save()
	                        logger.info("******************Albumart saved to {}*********************".format(name))
	                        shutil.move(os.path.realpath(os.path.join(root,name)), os.path.realpath(os.path.join('destination_folder',name)))
	                        
	                    except Exception as e:
	                        logger.error("Error in getting AlbumArt. Won't be saved to Tag - {}".format(name))
	                        logger.debug(e)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='This script scans a folder and finds and saves albumart to the songs. It also moves them to another folder if successful')
	parser.add_argument('-s','--source', help='Source folder. If empty will take the default one defined in script',required=False)
	parser.add_argument('-d','--destination',help='Completed Folder. If empty will take the default one defined in script', required=False)
	args = parser.parse_args()
	main(args.source or SOURCE_FOLDER ,args.destination or DESTINATION_FOLDER)
	 