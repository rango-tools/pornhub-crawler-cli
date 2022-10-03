__author__ = "Amirhossein Douzendeh Zenoozi"
__license__ = "MIT"
__version__ = "1.0"
__proxy__ = False
__doc__ = """
Pornhub CLI Crawler
Usage:
    pornhub.py model [--download=<folder-name>] [--browser] [--login] [--page=<page-number>] [--socks5=<proxy-addr>] [--spliter=<second>] <url>
    pornhub.py archive [--download=<folder-name>] [--browser] [--login] [--page=<page-number>] [--socks5=<proxy-addr>] [--spliter=<second>] <url>
    pornhub.py video [--download=<folder-name>] [--browser] [--login] [--socks5=<proxy-addr>] [--spliter=<second>] <videoID>
    pornhub.py -h | --help
    pornhub.py -v | --version

------------------------------------------------------------------

Options:
    --page=<page-number>        Total Pages.
    --socks5=<proxy-addr>       Socks5 Proxy Address.
    --browser                   Showing Browser if You Need.
    --login                     If The Login is Necessary.
    --download=<folder-name>    Download Video.
    --spliter=<second>          Splite Orginal Video By Action List
    -h --help                   Show this screen.
    -v --version                Show version.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from docopt import docopt
from dotenv import load_dotenv

import script.utils as ut
import urllib.request as req

import os
import youtube_dl
import time
import sqlite3
import json

load_dotenv()
UserName = os.getenv('PHUB_USERNAME')
PassWord = os.getenv('PHUB_PASSWORD')

class PornHubCrawler:
    def __init__(self, **kwargs):
        # DataBase Connection Config
        self.currentPath = os.path.abspath(os.getcwd())
        self.downloadPath = os.path.join( self.currentPath, self.enableDownload)
        self.dataBaseConnection = sqlite3.connect(f'{self.currentPath}/pornhub.db')
        self.spliterSecond = kwargs.get( 'spliterSecond', '')
        self.enableDownload = kwargs.get( 'enableDownload', False)
        self.showBrowser = kwargs.get('showBrowser', True)
        self.socks5 = kwargs.get( 'socks5', '' )
        self.youtubeDlOptions = {}
        
        try:
            self.dataBaseConnection.execute('''CREATE TABLE pornhub
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id CHAR(50),
                categories_list TEXT NOT NULL,
                actions_list TEXT NOT NULL,
                like_count INTEGER,
                dislike_count INTEGER,
                video_title TEXT NOT NULL);''')
        except sqlite3.Error as error:
            print(error)
            pass

        # Selenium Driver Options
        self.driverOption = webdriver.ChromeOptions()
        self.driverOption.add_argument('log-level=3')

        if (self.enableDownload and not os.path.exists(self.downloadPath)):
            os.makedirs(self.downloadPath)

        if( not self.showBrowser ):
            self.driverOption.add_argument('headless')

        if( socks5 := self.socks5 ):
            self.driverOption.add_argument( f'--proxy-server=socks5://{socks5}')
            self.youtubeDlOptions['proxy'] = f'socks5://{socks5}'

        self.driver = webdriver.Chrome( options = self.driverOption )
        self.driver.maximize_window()

    def login( self ):
        loginUrl = 'https://www.pornhub.com/login'
        self.driver.get( loginUrl )
        loginWait = WebDriverWait( self.driver, 10)
        username = self.driver.find_element(By.ID, 'username')
        password = self.driver.find_element(By.ID, 'password')
        submit = self.driver.find_element(By.ID, 'submit')

        # Clear Input Fields
        username.clear()
        password.clear()
        
        # Set Input Fields Value
        username.send_keys(UserName)
        password.send_keys(PassWord)
        
        # Submit Form
        loginWait.until( EC.element_to_be_clickable((By.ID, 'submit')) )
        self.driver.execute_script('arguments[0].scrollIntoView();', submit)
        self.driver.find_element(By.CSS_SELECTOR, '.js-loginSubmit[value="Log In"]').click()
        
        # Wait To Login Request Complete
        self.driver.implicitly_wait(10)
        time.sleep(10)

    def download_single_video( self, pageUrl ):
        self.youtubeDlOptions['outtmpl'] = f'{self.downloadPath}/%(id)s/%(id)s.%(ext)s'
        with youtube_dl.YoutubeDL( self.youtubeDlOptions ) as ydl:
            ydl.download([pageUrl])

    def process_model_page( self, modelPageUrl, toPage):
        for pageNumber in range(toPage or 1):
            modelPageUrl = f'{modelPageUrl}?page={pageNumber + 1}'
            self.driver.get( modelPageUrl )

            # Get Single Model Page Video ID's
            videosWrapperElem = [v.get_attribute('_vkey') for v in self.driver.find_elements_by_css_selector('ul#mostRecentVideosSection li.pcVideoListItem.videoBox')]
            for videoID in videosWrapperElem:
                print(f'=========== Start Checking Video: {videoID} ===========\n')
                self.process_single_video( videoID )

    def split_video_by_Actions( self, actionList, videoName, second ):
        spliteSecond = int( second ) if second != '' else 5
        fileItem = f'{videoName}/{os.listdir(videoName)[0]}'
        if( fileItem.startswith( videoName ) ):
            for action in actionList:
                splittedFileName = fileItem.rsplit('.', 1)
                newFileName = splittedFileName[0] + '-' + action["name"].lower() + '.' + splittedFileName[1]
                os.system( f'ffmpeg -i "{fileItem}" -ss { int( action["time"] ) - spliteSecond } -t {spliteSecond*2} { newFileName }')

    def process_archive_page( self, archiveUrl, toPage ):
        for pageNumber in range(toPage or 1):
            archiveUrl = f'{archiveUrl}?page={pageNumber + 1}'
            self.driver.get( archiveUrl )

            # Get Single Archive Page Video ID's
            videosWrapperElem = [v.get_attribute('_vkey') for v in self.driver.find_elements_by_css_selector('ul#videoCategory li.pcVideoListItem.videoBox')]
            for videoID in videosWrapperElem:
                print(f'=========== Start Checking Video: {videoID} ===========\n')
                self.process_single_video( videoID )
            
    def process_single_video( self, videoID ):
        if (self.is_video_processed(videoID)):
            generatedVideoUrl = f'https://www.pornhub.com/view_video.php?viewkey={videoID}'
            self.driver.get(generatedVideoUrl)
            
            # Empty Lists
            videoTitle = ''
            likeCount = ''
            disLikeCount = ''
            videoCategories = []
            videoActions = []
            downloadLinks = []

            # Get Actions List
            for index, action in enumerate(self.driver.find_elements(By.CSS_SELECTOR, 'div.seconds ul.actionTagList a li')):
                actionName = self.driver.execute_script('return arguments[0].firstChild.textContent;', action).strip().lower().replace(' ', '_')
                actionTime = ut.convert_minute_to_seconds( self.driver.execute_script('return arguments[0].childNodes[1].textContent;', action).strip())
                actionObject = { "name": f'{actionName}_{index}', "time": actionTime }
                videoActions.append( actionObject )

            if len(videoActions):
                # Get Title / Like Counte / Dislike Counte
                videoTitle = self.driver.find_element(By.CSS_SELECTOR, 'h1.title').text
                likeCount = int( self.driver.find_element(By.CSS_SELECTOR, 'span.votesUp').get_attribute('data-rating') )
                disLikeCount = int( self.driver.find_element(By.CSS_SELECTOR, 'span.votesDown').get_attribute('data-rating') )

                # Get Categories List
                for cat in self.driver.find_elements(By.CSS_SELECTOR, 'div.categoriesWrapper a.item'):
                    videoCategories.append( cat.text )

                # Check The User is Logged In Or Not!
                if( 'logged-in' in self.driver.find_element(By.CSS_SELECTOR, 'body').get_attribute('class').split() ):
                    # Check The Download File is Free or Not!
                    if 'js-paidDownload' not in self.driver.find_element(By.CSS_SELECTOR, 'div.tab-menu-wrapper-row div:nth-child(2)').get_attribute('class').split():
                        for link in self.driver.find_elements(By.CSS_SELECTOR, 'div.download-tab a'):
                            downloadLinkType = self.driver.execute_script('return arguments[0].childNodes[2].textContent;', link).strip()
                            downloadLink = link.get_attribute('href')
                            downloadObject = { "type": downloadLinkType, "link": downloadLink }
                            downloadLinks.append( downloadObject )
                    else:
                        print('=========== We Need Permium Account! ===========')
                else:
                    print('==== You Need To Logged In To Your Account! ====')

                if( self.enableDownload ):
                    self.download_single_video( generatedVideoUrl )

                if( second := self.spliterSecond ):
                    self.split_video_by_Actions( videoActions, videoID, second )
                    
                self.insert_item_to_database( videoID, json.dumps(videoCategories), json.dumps(videoActions), likeCount, disLikeCount, videoTitle )
        else:
            print(f'=========== This Video is already proccessed! ===========')

    def is_video_processed( self, videoID ):
        database_record = self.dataBaseConnection.execute("""SELECT video_id FROM pornhub WHERE video_id = (?) LIMIT 1""", (videoID,)).fetchone()
        return not database_record

    def insert_item_to_database( self, videoID, categoriesList, actionsList, likeCount, dislikeCount, videoTitle ):
        try:
            self.dataBaseConnection.execute("""INSERT INTO pornhub (video_id, categories_list, actions_list, like_count, dislike_count, video_title) VALUES (?, ?, ?, ?, ?, ?)""", (videoID, categoriesList, actionsList, likeCount, dislikeCount, videoTitle))
            self.dataBaseConnection.commit()
        except sqlite3.Error as error:
            print(error)
            pass

    def close_driver( self ):
        self.dataBaseConnection.close()
        self.driver.close()
        self.driver.quit()

def init():
    arguments = docopt(__doc__, version='v1.0')
    enableDownload = arguments['--download'] if arguments['--folder-name '] else 'downloads'
    pageNumber = arguments['--page'] if arguments['--page-count'] else 1
    socks5Proxy = arguments['--socks5']
    showBrowser = arguments['--browser']
    spliterSecond = arguments['--spliter']
    needLogin = arguments['--login']
    pageUrl = arguments['<url>']
    videoID = arguments['<videoID>']

    pornHub = PornHubCrawler( socks5=socks5Proxy, showBrowser=showBrowser, spliterSecond=spliterSecond, enableDownload=enableDownload )

    if( needLogin ):
        pornHub.login()

    if ( arguments['video'] ):
        pornHub.process_single_video( videoID=videoID )
    elif ( arguments['model'] ):
        pornHub.process_model_page( pageUrl, toPage=pageNumber )
    elif ( arguments['archive'] ):
        pornHub.process_archive_page( pageUrl, toPage=pageNumber )
    
    pornHub.close_driver()

if __name__ == '__main__':
    init()
