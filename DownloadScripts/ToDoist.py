from todoist.api import TodoistAPI
from MusicTools import MusicTools


import configparser
import json

import logging
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
class ToDoistWalker:


    # PROJECT_NAME = 'Inbox'
    # TODOIST_API_KEY = '5e47c308c0e4bea68d7af794e2ec59ef5a541deb'

    def __init__(self):
        ### LOADING THE CONFIG VARIABLES FROM FILE
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
        except:
            with open('../config.json', 'r') as f:
                config = json.load(f)

        self.PROJECT_NAME = config['TODOIST']['PROJECT_NAME']
        self.TODOIST_API_KEY = config['TODOIST']['TODOIST_API_KEY']

        self.api = TodoistAPI(self.TODOIST_API_KEY)
        self.api.sync()

    def find_project_id_by_name(self,project_name):
        projects = self.api.state['projects']
        for project in projects:
            if project['name'] == project_name:
                return project['id']

    def walk_items_in_project(self):
        items = self.api.state['items']
        mt = MusicTools()
        result = 1
        song_list = []
        logger.info("Scanning and Downloading ToDoist List:{}".format(self.PROJECT_NAME))
        for item in items:
            song_dict = {}
            logger.debug(u"Scanning {}|{}".format(item['content'], item['id']))
            if ((item['project_id'] == self.find_project_id_by_name(self.PROJECT_NAME)) & (item['checked']==0)): #For Debug  & (item['id']==112286022)    
                #print(item['content'] + "|" + str(item['id']))
                song_dict = self.get_song_dict(item['content'],mt)
                if song_dict:
                    song_list.append(song_dict)
                    logger.info(u"Scanned Results: {}|{}".format(song_dict['title'], song_dict['link']))
                    result = mt.download_music(song_dict['link'], song_dict['title'], is_quiet=True)
                    # result = 1
                    logger.debug("Download Result: {} | 1 is a failure, 0 is a success".format(result))
                #1 is a failure, 0 is a success
                    if result == 0:
                        logger.info("Download Success. Marking item as completed...")
                        item.complete()
                        mt.fix_id3(song_dict['title'])
                    else:
                        logger.error(u"Downloading of {} failed. Moving to the next item...".format(song_dict['title']))
        self.api.commit()




    def get_song_dict(self,item,mt):
        # mt = MusicTools()
        #Checking Youtube Links
        song_dict ={}

        link = mt.get_youtube_link_from_item(item)
        if link:
            vid_code = mt.get_youtube_code_from_link(link)
            if vid_code:
                link = 'https://www.youtube.com/watch?v={}'.format(vid_code)
                title = mt.get_clean_title(mt.get_title_youtube(vid_code))
        else:
            link = mt.get_soundcloud_link_from_item(item)
            if link:
                title = mt.get_clean_title(mt.get_title_soundcloud(link))
            else:
                #Items without a link
                song_dict = mt.youtube_search(item,1)
                if len(song_dict) >0 :
                    return mt.youtube_search(item,1)[0]
                else:
                    return None
        song_dict['link'] = link
        song_dict['title'] = title
        return song_dict

import argparse

def main():
   todoist_walker = ToDoistWalker()
   todoist_walker.walk_items_in_project()
   logger.info('*************************ToDoist Download Finished***************************')
   
if __name__ == '__main__':
   parser = argparse.ArgumentParser(description='This is a script to download the songs I have added to ToDoist')
   args = parser.parse_args()
   main()