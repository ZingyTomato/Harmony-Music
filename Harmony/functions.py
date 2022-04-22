import os
from termcolor import colored
import time
import requests
import json
import songs
import videos
import albums
import playlists

queue_list = []

item_list = []

headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
}

YOUTUBE_REGEX = r"http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?"

URL_REGEX = r"(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?"

PLAYLIST_REGEX = r" /^.*(youtu.be\/|list=)([^#\&\?]*).*/"

def emptyQueue():
    item_list.clear()
    queue_list.clear()

def youtubeLink():
    info = print(colored("\nYoutube URL detected, directly playing the link.", color='cyan', attrs=['bold'])  + colored(' (q to quit)\n', 'red'))
    return info

def urlLink():
    info = print(colored("\nURL detected, trying to directly play the link.", color='cyan', attrs=['bold'])  + colored(' (q to quit)\n', 'red'))
    return info

def playlistLink():
    info = print(colored("\nLinks are not supported. Use --playlist to search for playlists.", color='red', attrs=['bold'])  + colored(' (q to quit)\n', 'red'))
    return info

def albumLink():
    info = print(colored("\nLinks are not supported. Use --album to search for albums.", color='red', attrs=['bold'])  + colored(' (q to quit)\n', 'red'))
    return info

def invalidString():
    exitmsg = print(colored("\nPlease enter a valid string!\n", 'red', attrs=['bold']))
    return exitmsg

def invalidInteger():
    exitmsg = print(colored("\nPlease enter a valid integer!", 'red', attrs=['bold']))
    return exitmsg

def exitProgram():
    exitmsg = print(colored("\nExited.\n", 'red', attrs=['bold']))
    return os.system("exit"), exitmsg

def noResults(result):
    info = print(colored(f"Unable to find any results for {colored(result, 'cyan')}! \n", 'red', attrs=['bold']))
    return info

def invalidRange():
    exitmsg = print(colored("\nInteger out of range!", 'red', attrs=['bold']))
    return exitmsg

def showQueue(item_list):
    if len(item_list) == 0:
      empty = print(colored("\nThe queue is empty!\n",'red', attrs=['bold']))
      return empty
    else:
      show_queue = print(f"\n".join([f"{colored(i, 'green')}. {track} \n" for i, track in enumerate((item_list))]))     
      return show_queue

def showResults(query, result):
    info = print(colored("Results for", 'red') + colored(f" {query}\n", 'cyan', attrs=['bold']))
    lists = print(f"\n".join([f"{colored(i, 'green')}. {item['title']} - {item['uploaderName']} ({time.strftime('%M:%S',time.gmtime(item['duration']))})" for i, item in enumerate((result['items']))]))
    return info, lists

def showResultsAlbumsPlaylists(query, result):
    info = print(colored("Results for", 'red') + colored(f" {query}\n", 'cyan', attrs=['bold']))
    lists = print(f"\n".join([f"{colored(i, 'green')}. {item['name']} - {item['uploaderName']}" for i, item in enumerate((result['items']))]))
    return info, lists

def getSongs(query):
    print(colored("\nSearching for songs... \n", 'cyan', attrs=['bold']))
    searchurl = requests.request("GET", f"https://pipedapi.kavin.rocks/search?q={query}&filter=music_songs", headers=headers).text
    searchjson = json.loads(searchurl)
    return searchjson

def getVideos(query):
    print(colored("\nSearching for videos... \n", 'cyan', attrs=['bold']))
    searchurl = requests.request("GET", f"https://pipedapi.kavin.rocks/search?q={query}&filter=videos", headers=headers).text
    searchjson = json.loads(searchurl)
    return searchjson

def getAlbums(query):
    print(colored("\nSearching for albums... \n", 'cyan', attrs=['bold']))
    searchurl = requests.request("GET", f"https://pipedapi.kavin.rocks/search?q={query}&filter=music_albums", headers=headers).text
    searchjson = json.loads(searchurl)
    return searchjson

def getPlaylists(query):
    print(colored("\nSearching for playlists... \n", 'cyan', attrs=['bold']))
    searchurl = requests.request("GET", f"https://pipedapi.kavin.rocks/search?q={query}&filter=playlists", headers=headers).text
    searchjson = json.loads(searchurl)
    return searchjson
    
def playTracks(item_list, queue_list):
    if len(item_list) == 0:
      empty = print(colored("\nThe queue is empty!\n",'red', attrs=['bold']))
      return empty
    queuemsg = print(colored("\nPlaying items in the queue", 'cyan', attrs=['bold']) + colored(' (q to quit)\n', 'red')) 
    show_queue = print(f"\n".join([f"{colored(i, 'green')}. {track} \n" for i, track in enumerate((item_list))]))     
    play_tracks = os.system(f"mpv --vo=null --cache=yes --video=no --no-video --term-osd-bar --no-resume-playback {' '.join(queue_list)} ")
    return queuemsg, show_queue, play_tracks

def playVideos(item_list, queue_list):
    if len(item_list) == 0:
      empty = print(colored("\nThe queue is empty!\n",'red', attrs=['bold']))
      return empty
    queuemsg = print(colored("\nPlaying items in the queue", 'cyan', attrs=['bold']) + colored(' (q to quit)\n', 'red')) 
    show_queue = print(f"\n".join([f"{colored(i, 'green')}. {track} \n" for i, track in enumerate((item_list))]))     
    play_videos = os.system(f"mpv --cache=yes --term-osd-bar --no-resume-playback {' '.join(queue_list)} ")
    return queuemsg, show_queue, play_videos

def playVideosURL(url):
    play_videos = os.system(f"mpv --cache=yes --term-osd-bar --no-resume-playback {url} ")
    return play_videos

def playTracksURL(url):
    play_videos = os.system(f"mpv --vo=null --cache=yes --video=no --no-video --term-osd-bar --no-resume-playback {url} ")
    return play_videos

def addItems(videoid, title, author):
    stream_url = "https://piped.kavin.rocks" + f"{videoid}"
    queue_list.append(stream_url)
    item_list.append(f"{title} - {author}")
    added = print(colored(f"\n{title} - ", 'cyan') + colored(f'{author}', 'red') + colored(" has been added to the queue.\n", 'green'))
    return added

def chooseOption():
    option = input(colored("\nSelect an option ", 'cyan', attrs=['bold']) + colored("(S)ongs, (V)ideos, (P)laylists, (A)lbums, Q(uit): ", 'red'))
    if option == "S" or option == "s":
        return print("\n"), songs.searchSongs()
    elif option == "V" or option == "v":
        return print("\n"), videos.searchVideos()
    elif option == "P" or option == "p":
        return print("\n"), playlists.searchPlaylists()
    elif option == "A" or option == "a":
        return print("\n"), albums.searchAlbums()
    elif option == "Q" or option == "q" or option == "B" or option == "b":
        return exitProgram()
    else:
        info = print(colored("\nInvalid option entered!", 'red', attrs=['bold'])) 
        return info, chooseOption()
    return