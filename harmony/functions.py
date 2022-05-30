import os
from termcolor import colored
import time
import requests
import json
import songs
import videos
import re
import sys
import signal
import html

queue_list = []

item_list = []

audio_list = []

title_list = []

author_list = []

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'}

YOUTUBE_REGEX = r"http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?"

URL_REGEX = r"(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?"

SEARCH_URL = "https://saavn.me"

PIPEDAPI_URL = "https://pipedapi.kavin.rocks"

PIPED_URL = "https://piped.kavin.rocks"

LYRICS_API = "https://api.textyl.co/api"

SUB_FILE = ""

def emptyQueue():
    item_list.clear()
    queue_list.clear()
    audio_list.clear()
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

def noStreamUrl():
    info = print(colored(f"\nUnable to find any a stream URL!", 'red', attrs=['bold']))
    return 

def invalidRange():
    exitmsg = print(colored("\nInteger out of range!", 'red', attrs=['bold']))
    return 

def queueIsEmpty():
    empty = print(colored("\nThe queue is empty!",'red', attrs=['bold']))
    return 

def fixFormatting(text):
      inital_text = html.unescape(f'{text}')
      final_text = re.sub("[\"\']", " ", inital_text)
      return final_text

def emptyInput():
    print(colored("\nPlease enter the name of a song!", 'red', attrs=['bold']))
    return

def showQueue():
    if len(item_list) == 0:
      return queueIsEmpty()
    else:
      show_queue = print(f"\ns".join([f"\n{colored(i, 'green')}. {fixFormatting(track)}" for i, track in enumerate((item_list), start=1)]))     
      return 

def showResults(query, result):
    info = print(colored("Results for", 'red') + colored(f" {query}\n", 'cyan', attrs=['bold']))
    lists = print(f"\n".join([f"{colored(i, 'green')}. {colored(fixFormatting(item['name']), 'red', attrs=['bold'])} - {colored(fixFormatting(item['artist']), 'cyan', attrs=['bold'])} ({time.strftime('%M:%S',time.gmtime(int(item['duration'])))})" for i, item in enumerate((result['results']), start=1)]))
    return songs.pickTrack(query, result)

def showResultsVideos(query, result):
    info = print(colored("Results for", 'red') + colored(f" {query}\n", 'cyan', attrs=['bold']))
    lists = print(f"\n".join([f"{colored(i, 'green')}. {colored(fixFormatting(item['title']), 'red', attrs=['bold'])} - {colored(fixFormatting(item['uploaderName']), 'cyan', attrs=['bold'])} ({time.strftime('%M:%S',time.gmtime(item['duration']))})" for i, item in enumerate((result['items']), start=1)]))
    return videos.pickVideo(query, result)

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
    print(colored("\nSearching for songs...", 'cyan', attrs=['bold']))
    searchurl = requests.request("GET", f"{SEARCH_URL}/search/songs?query={query}&page=1&limit=20", headers=headers).text.encode()
    searchjson = json.loads(searchurl)
    if len(searchjson['results']) == 0:
        return noResults(query), songs.searchSongs()
    print(colored("\nFound results!", 'green', attrs=['bold']), end="\r")
    time.sleep(0.5)
    print(colored("Loading results...", 'green', attrs=['bold']), end="\r")
    time.sleep(0.5)
    return showResults(query, searchjson)

def getVideos(query):
    print(colored("\nSearching for videos...", 'cyan', attrs=['bold']))
    searchurl = requests.request("GET", f"{PIPEDAPI_URL}/search?q={query}&filter=videos", headers=headers).text.encode()
    searchjson = json.loads(searchurl)
    if len(searchjson['items']) == 0:
        return noResults(query), videos.searchVideos()
    print(colored("\nFound results!", 'green', attrs=['bold']), end="\r")
    time.sleep(0.5)
    print(colored("Loading results...", 'green', attrs=['bold']), end="\r")
    time.sleep(0.5)
    return showResultsVideos(query, searchjson)
    
def playTracks():
    if len(item_list) == 0:
      return queueIsEmpty()
    queuemsg = print(colored("\nPlaying songs in the Queue", 'cyan', attrs=['bold']) + colored(' (Q)uit, (L)oop, (J) Disable Lyrics\n', 'red')) 
    show_queue = print(f"\n".join([f"{colored(i, 'green')}. {fixFormatting(track)} \n" for i, track in enumerate((item_list), start=1)]))     
    print(colored("Launching MPV and searching for Lyrics...", 'green', attrs=['bold']), end="\r")
    for track, title, author in zip(queue_list, title_list, author_list):
        lyricsToVtt(f"{title} - {author}")
        os.system(f"mpv --no-video --term-osd-bar --no-resume-playback --term-playing-msg='{fixFormatting(colored(title, 'red'))} - {fixFormatting(colored(author, 'cyan'))}' '{track}' {SUB_FILE} ")
        removeSubs()
    return emptyQueue(), removeSubs(), songs.searchSongs()

def playVideos():
    if len(item_list) == 0:
      return queueIsEmpty()
    queuemsg = print(colored("\nPlaying videos in the Queue", 'cyan', attrs=['bold']) + colored(' (Q)uit, (L)oop\n', 'red')) 
    show_queue = print(f"\n".join([f"{colored(i, 'green')}. {fixFormatting(track)} \n" for i, track in enumerate((item_list), start=1)]))     
    print(colored("Launching MPV...", 'green', attrs=['bold']), end="\r")
    play_videos = [os.system(f"mpv --term-osd-bar --no-resume-playback '{track}' --audio-file='{audio}' --force-media-title='{fixFormatting(title)}'") for track, audio, title in zip(queue_list, audio_list, title_list)]
    return emptyQueue(), videos.searchVideos()

def playTracksURL(url):
    print(colored("Launching MPV...", 'green', attrs=['bold']), end="\r")
    play_videos = os.system(f"mpv --no-video --term-osd-bar --no-resume-playback {url} ")
    return songs.searchSongs()

def playVideosURL(url):
    print(colored("Launching MPV...", 'green', attrs=['bold']), end="\r")
    play_videos = os.system(f"mpv --no-resume-playback {url} ")
    return videos.searchVideos()

def addSongs(videoid, title, author):
    print(colored("\nGathering info...", 'green', attrs=['bold']), end="\r")
    queue_list.append(videoid)
    title_list.append(title)
    author_list.append(author)
    item_list.append(f"{colored(title, 'red')} - {colored(author, 'cyan')}")
    added = print(colored(f"{fixFormatting(title)} - ", 'cyan') + colored(f"{fixFormatting(author)}", 'red') + colored(" has been added to the queue.", 'green'))
    return songs.searchSongs()

def addVideos(videoid, title, author):
    print(colored("\nGathering info...", 'green', attrs=['bold']), end="\r")
    videoid = videoid.replace("/watch?v=", "")
    searchurl = requests.request("GET", f"{PIPEDAPI_URL}/streams/{videoid}", headers=headers).text.encode()
    searchjson = json.loads(searchurl)
    videourl = searchjson['videoStreams'][0]['url']
    audiourl = searchjson['audioStreams'][0]['url']
    queue_list.append(videourl)
    audio_list.append(audiourl)
    title_list.append(title)
    item_list.append(f"{colored(title, 'red')} - {colored(author, 'cyan')}")
    added = print(colored(f"{fixFormatting(title)} - ", 'cyan') + colored(f'{fixFormatting(author)}', 'red') + colored(" has been added to the queue.", 'green'))
    return videos.searchVideos()

def parseTime(s):
    return time.strftime('%H:%M:%S.%MS',time.gmtime(s))

def lyricsToVtt(query):
    global SUB_FILE
    try:
      data = requests.request("GET", f"{LYRICS_API}/lyrics?q={fixFormatting(query)}", headers=headers).text.encode()
      data = json.loads(data)
      SUB_FILE = "--sub-file=subs.vtt"
    except:
      SUB_FILE = ""
      return
    with open("subs.vtt", "w") as file:
        file.write("WEBVTT")
        file.write("\n")
        for i,v in enumerate(data):
          try:
            file.write("\n")
            file.write(f"{parseTime(v['seconds'])} --> {parseTime(data[i + 1]['seconds'])}")
            file.write("\n")
            file.write(f"♪ {v['lyrics']} ♪".upper())
            file.write("\n")
          except IndexError:
            return

signal.signal(signal.SIGINT, forceQuit)