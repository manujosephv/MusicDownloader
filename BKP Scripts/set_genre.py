
import os
import eyed3
from MusicTools import MusicTools
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


folder = 'D:\Music Download\downloaded_music - Copy'
mt = MusicTools()
for root, dirs, files in os.walk(folder):
    for name in files:
        dict_file = {}
        if name.endswith((".mp3")):
            logger.debug('File: {}'.format(name))
            mp3 = eyed3.load(os.path.realpath(os.path.join(root,name)))
            # print ("File: {}".format(name))
            genre = mt.get_genre_from_last_fm(mp3)
            logger.debug('Genre: {}'.format(genre))
            if genre == 'Unavailable':
                logger.info(u'Genre not available for {} - {}'.format(mp3.tag.artist, mp3.tag.title))
            if mp3.tag:
                mp3.tag.genre = unicode(genre)
            else:
                mp3.tag = eyed3.id3.Tag()
                mp3.tag.genre = unicode(genre)
            mp3.tag.save()
