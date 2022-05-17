import os
from termcolor import colored
import time
import requests
import json
import songs
import re

queue_list = []

item_list = []

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'}

YOUTUBE_REGEX = r"http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?"

URL_REGEX = r"(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?"

SEARCH_URL = "https://saavn.me"

def emptyQueue():
    item_list.clear()
    queue_list.clear()

def youtubeLink(url):
    info = print(colored("\nYoutube URL detected, directly playing the link.", color='cyan', attrs=['bold'])  + colored(' (q to quit)\n', 'red'))
    return playTracksURL(url)

def urlLink(url):
    info = print(colored("\nURL detected, trying to directly play the link.", color='cyan', attrs=['bold'])  + colored(' (q to quit)\n', 'red'))
    return playTracksURL(url)

def invalidInput():
    exitmsg = print(colored("\nInvalid input Entered!", 'red', attrs=['bold']))
    return 

def exitProgram():
    exitmsg = print(colored("\nExited.\n", 'red', attrs=['bold']))
    return 

def noResults(result):
    info = print(colored(f"\nUnable to find any results for {colored(result, 'cyan')}!", 'red', attrs=['bold']))
    return songs.searchSongs()

def invalidRange():
    exitmsg = print(colored("\nInteger out of range!", 'red', attrs=['bold']))
    return 

def queueIsEmpty():
    empty = print(colored("\nThe queue is empty!",'red', attrs=['bold']))
    return songs.searchSongs()

def fixTitle(title):
    final_title = re.sub("[\"\']", " ", title)
    return final_title

def showQueue():
    if len(item_list) == 0:
      return queueIsEmpty()
    else:
      show_queue = print(f"\n".join([f"\n{colored(i, 'green')}. {track}" for i, track in enumerate((item_list), start=1)]))     
      return songs.searchSongs()

def showResults(query, result):
    info = print(colored("Results for", 'red') + colored(f" {query}\n", 'cyan', attrs=['bold']))
    lists = print(f"\n".join([f"{colored(i, 'green')}. {colored(item['name'], 'red', attrs=['bold'])} - {colored(item['artist'], 'cyan', attrs=['bold'])} ({time.strftime('%M:%S',time.gmtime(int(item['duration'])))})" for i, item in enumerate((result['results']), start=1)]))
    return songs.pickTrack(query, result)

def getSongs(query):
    print(colored("\nSearching for songs...", 'cyan', attrs=['bold']))
    searchurl = requests.request("GET", f"{SEARCH_URL}/search/songs?query={query}&page=1&limit=20", headers=headers).text.encode()
    searchjson = json.loads(searchurl)
    if len(searchjson['results']) == 0:
        return noResults(query)
    print(colored("\nFound results!", 'green', attrs=['bold']), end="\r")
    time.sleep(0.5)
    print(colored("Loading results...", 'green', attrs=['bold']), end="\r")
    time.sleep(0.5)
    return showResults(query, searchjson)
    
def playTracks():
    if len(item_list) == 0:
      return queueIsEmpty()
    queuemsg = print(colored("\nPlaying songs in the queue", 'cyan', attrs=['bold']) + colored(' (Q)uit\n', 'red')) 
    show_queue = print(f"\n".join([f"{colored(i, 'green')}. {track} \n" for i, track in enumerate((item_list), start=1)]))     
    print(colored("Launching MPV...", 'green', attrs=['bold']), end="\r")
    play_tracks = [os.system(f"mpv --vo=null --cache=yes --video=no --no-video --term-osd-bar --term-playing-msg='{fixTitle(title)}' --no-resume-playback '{track}' ") for track, title in zip(queue_list, item_list)]
    return emptyQueue(), songs.searchSongs()

def playTracksURL(url):
    print(colored("Launching MPV...", 'green', attrs=['bold']), end="\r")
    play_videos = os.system(f"mpv --vo=null --cache=yes --video=no --no-video --term-osd-bar --no-resume-playback {url} ")
    return songs.searchSongs()

def addSongs(videoid, title, author):
    queue_list.append(videoid)
    item_list.append(f"{colored(title, 'red')} - {colored(author, 'cyan')}")
    added = print(colored(f"\n{title} - ", 'cyan') + colored(f'{author}', 'red') + colored(" has been added to the queue.", 'green'))
    return added, songs.searchSongs()
