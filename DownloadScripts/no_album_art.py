
import os
import shutil
import eyed3
import json
import argparse
import codecs

import logging
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

### LOADING THE CONFIG VARIABLES FROM FILE
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except:
    with open('../config.json', 'r') as f:
        config = json.load(f)

def main(scan_folder=None,move_folder=None):
    logger.info('Scanning the folder')
    ACTION_FAILED_FILE_NAME = os.path.join(config['DEFAULT']['ROOT'],config['DEFAULT']['ACTION_FAILED_FILE_NAME'])
    if ((scan_folder is None) | (move_folder is None)):
        scan_folder = os.path.join(config['DEFAULT']['ROOT'],os.path.basename(config['MUSICTOOLS']['DOWNLOAD_PATH']))
        move_folder = os.path.join(config['DEFAULT']['ROOT'],'No AlbumArt')
    # scan_folder = 'D:\Music Download\downloaded_music'
    # move_folder = 'D:\Music Download\No Albumart'
    print scan_folder
    print move_folder
    for root, dirs, files in os.walk(scan_folder):
        for name in files:
            if name.endswith((".mp3")):
                logger.info(u'Scanning {}'.format(name))
                try:
                    mp3 = eyed3.load(os.path.realpath(os.path.join(root,name)))
                    # print ("File: {}".format(name))
                    if mp3.tag:
                        if len( mp3.tag.images ) == 0:
                            # print ("No AlbumArt")
                            logger.info(u'No AlbumArt. Moving {}'.format(name))
                            shutil.move(os.path.realpath(os.path.join(root,name)), os.path.realpath(os.path.join(move_folder,name)))
                except ValueError:
                    
                    logger.error(u"Unable to load mp3 for {}. Moving to the next file...".format(name))
                    with codecs.open(ACTION_FAILED_FILE_NAME,encoding='utf-8', mode='a+') as f:
                        f.write(u"{}\n".format(name))
    logger.info('Finished Moving')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This is a script to identify and move the mp3 files without an album art to another folder.')
    parser.add_argument('-s','--scan', type=str,help='This specifies the folder to scan. By default it is set to {}'.format(os.path.join(config['DEFAULT']['ROOT'],os.path.basename(config['MUSICTOOLS']['DOWNLOAD_PATH']))), required=False)
    parser.add_argument('-m','--move', type=str,help='This specifies the folder the files are moved. By default it is set to {}'.format(os.path.join(config['DEFAULT']['ROOT'],'No AlbumArt')), required=False)
    args = parser.parse_args()
    print args.scan
    print args.move
    main(args.scan, args.move)