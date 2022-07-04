import os
from termcolor import colored
import time
import requests
import json
import songs
import re
import sys
import signal
import html
import lyrics

queue_list = []

item_list = []

audio_list = []

title_list = []

author_list = []

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'}

YOUTUBE_REGEX = r"http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?"

URL_REGEX = r"(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?"

SEARCH_URL = "https://saavn.me"

LYRICS_API = "https://api.textyl.co/api"

TRENDING_API = "https://charts-spotify-com-service.spotify.com/public/v0/charts"

SUB_FILE = ""

def emptyQueue():
    item_list.clear()
    queue_list.clear()
    title_list.clear()
    author_list.clear()

def youtubeLink():
    info = print(colored("\nYoutube URL detected, directly playing the link.", color='cyan', attrs=['bold'])  + colored(' (q to quit)\n', 'red'))
    return 

def urlLink():
    info = print(colored("\nURL detected, trying to directly play the link.", color='cyan', attrs=['bold'])  + colored(' (q to quit)\n', 'red'))
    return 

def invalidInput():
    exitmsg = print(colored("\nInvalid input Entered!", 'red', attrs=['bold']))
    return 

def exitProgram():
    exitmsg = colored("\nExited.\n", 'red', attrs=['bold'])
    return sys.exit(exitmsg)

def noResults(result):
    info = print(colored(f"\nUnable to find any results for {colored(result, 'cyan')}!", 'red', attrs=['bold']))
    return 

def apiFailure():
    info = print(colored("Unable to search for any songs! Please try again later."))
    return 

def noStreamUrl():
    info = print(colored(f"\nUnable to find a stream URL for the specific song!", 'red', attrs=['bold']))
    return 

def invalidRange():
    exitmsg = print(colored("\nInteger out of range!", 'red', attrs=['bold']))
    return 

def queueIsEmpty():
    empty = print(colored("\nThe queue is empty!",'red', attrs=['bold']))
    return 

def fixFormatting(text):
    inital_text = html.unescape(f'{text}')
    final_text = re.sub("[\"\']", "", inital_text)
    return final_text

def isExplicit(value):
    if value == 1:
        explicit = colored("(E)", 'green')
        return explicit
    else:
        return ""

def emptyInput():
    print(colored("\nPlease enter the name of a song!", 'red', attrs=['bold']))
    return

def queueMessageSongs():
    queuemsg = print(colored("\nPlaying songs in the Queue", 'cyan', attrs=['bold']) + colored(' (Q)uit, (L)oop, (J) Disable Lyrics', 'red')) 
    return queuemsg

def clearScreen():
    return os.system("clear")

def removeSongs():
    try:
        item_list.pop(0)
        if len(item_list) == 0:
            return
        return clearScreen(), queueMessageSongs(), showQueue()
    except:
        return 

def showQueue():
    if len(item_list) == 0:
      return queueIsEmpty()
    else:
      show_queue = print(f"\n".join([f"\n{colored(i, 'green')}. {fixFormatting(track)}" for i, track in enumerate((item_list), start=1)]))     
      return 

def showResults(query, result):
    info = print(colored("Results for", 'red') + colored(f" {query}\n", 'cyan', attrs=['bold']))
    lists = print(f"\n".join([f"{colored(i, 'green')}. {colored(fixFormatting(item['name']), 'red', attrs=['bold'])} - {colored(fixFormatting(item['primaryArtists']), 'cyan', attrs=['bold'])} ({time.strftime('%M:%S',time.gmtime(int(item['duration'])))}) {isExplicit(int(item['explicitContent']))}" for i, item in enumerate((result['results']), start=1)]))
    return songs.pickTrack(query, result)

def forceQuit(signum, frame):
    print(colored("\nForce quit by user.", 'red', attrs=['bold']))
    removeSubs()
    return sys.exit(1)  

def removeSubs():
    try:
        os.remove('subs.vtt')
        return
    except:
        return

def getSongs(query):
    clearScreen()
    print(colored("\nSearching for songs...", 'cyan', attrs=['bold']))
    searchurl = requests.request("GET", f"{SEARCH_URL}/search/songs?query={query}&page=1&limit=20", headers=headers).text.encode()
    searchjson = json.loads(searchurl)
    if len(searchjson['results']) == 0:
        return noResults(query), songs.searchSongs()
    elif searchjson['status'] == "FAILED":
        return apiFailure(), songs.searchSongs()
    print(colored("\nFound results!", 'green', attrs=['bold']), end="\r")
    time.sleep(0.5)
    print(colored("Loading results...", 'green', attrs=['bold']), end="\r")
    time.sleep(0.5)
    return showResults(query, searchjson)
    
def playTracks():
    if len(item_list) == 0:
      return queueIsEmpty()
    clearScreen()
    queueMessageSongs()
    showQueue()
    print(colored("\nLaunching MPV and searching for Lyrics...", 'green', attrs=['bold']), end="\r")
    for track, title, author in zip(queue_list, title_list, author_list):
        lyrics.searchLyrics(f"{fixFormatting(title)} - {fixFormatting(author)}")
        os.system(f"mpv --no-video --term-osd-bar --no-resume-playback {SUB_FILE} --term-playing-msg='{fixFormatting(colored(title, 'red'))} - {fixFormatting(colored(author, 'cyan'))}' '{track}'")
        removeSubs()
    return emptyQueue(), removeSubs(), songs.searchSongs()

def playTracksURL(url):
    clearScreen()
    print(colored("Launching MPV...", 'green', attrs=['bold']), end="\r")
    play_videos = os.system(f"mpv --no-video --term-osd-bar --no-resume-playback {url} ")
    return songs.searchSongs()

def addSongs(videoid, title, author, duration, explicit):
    queue_list.append(videoid)
    title_list.append(title)
    author_list.append(author)
    item_list.append(f"{colored(title, 'red')} - {colored(author, 'cyan')} ({duration}) {explicit}")
    added = print(colored(f"\n{fixFormatting(title)} - ", 'cyan') + colored(f"{fixFormatting(author)}", 'red') + colored(" has been added to the queue.", 'green'))
    return songs.searchSongs()

def getTrending():
    clearScreen()
    print(colored("\nSearching for trending tracks...\n", 'cyan', attrs=['bold']))
    searchurl = requests.request("GET", f"{TRENDING_API}", headers=headers).text.encode()
    searchjson = json.loads(searchurl)
    return showTrending(searchjson)

def showTrending(result):
    lists = print(f"\n".join([f"{colored(i, 'green')}. {colored(fixFormatting(item['trackMetadata']['trackName']), 'red', attrs=['bold'])} - {fixFormatting(colored(item['trackMetadata']['artists'][0]['name'], 'cyan'))}" for i, item in enumerate((result['chartEntryViewResponses'][0]['entries']), start=1)]))
    return 

signal.signal(signal.SIGINT, forceQuit)