import requests
import json
import re
from termcolor import colored
import functions

def searchVideos():
  video = input(colored("\nAdd videos to the Queue ", 'cyan', attrs=['bold']) + colored("(P)lay, (S)how Queue, (B)ack, (Q)uit: ", 'red'))
  
  if re.match(functions.YOUTUBE_REGEX, video):
    return functions.youtubeLink(), functions.playVideosURL(video), searchVideos()

  elif re.match(functions.URL_REGEX, video):
    return functions.urlLink(), functions.playVideosURL(video), searchVideos()

  elif re.match(functions.PLAYLIST_REGEX, video):
    return functions.playlistLink(), searchVideos()

  if video.isnumeric() == True:
    return functions.invalidInput(), searchVideos()
    
  elif video == "q" or video == "Q":
    return functions.exitProgram()

  elif video == "b" or video == "B":
    return functions.emptyQueue(), functions.chooseOption()
      
  elif video == "p" or video == "P":
    return functions.playVideos(), functions.emptyQueue(), searchVideos()
      
  elif video == "s" or video == "S":
    return functions.showQueue(), searchVideos()
      
  return listVideos(video)

def listVideos(video):
  search_results = functions.getVideos(video)

  if re.match(functions.YOUTUBE_REGEX, video):
    return functions.youtubeLink(), functions.playVideosURL(video), searchVideos()
  
  elif re.match(functions.URL_REGEX, video):
    return functions.urlLink(), functions.playVideosURL(video), searchVideos()

  if len(search_results['items']) == 0:
    return functions.noResults(video), searchVideos()
    
  return functions.showResults(video, search_results), pickVideo(search_results, video)

def pickVideo(json, video):
  item_length = len(json['items'])
  option = input(colored("\nPick an option", 'cyan', attrs=['bold']) + colored(f" [1:{item_length}, (B)ack, (Q)uit]: ", 'red'))

  if option.isnumeric() == False and option != "b" and option != "B" and option != "q" and option != "Q":
    return functions.invalidInput(), pickVideo(json, video)
    
  elif option == "b" or option == "B":
    return searchVideos()

  elif option == "q" or option == "Q":
    return functions.exitProgram()

  if int(option) > item_length or int(option) < 1:
    return functions.invalidRange(), pickVideo(json, video)
      
  videoid = json['items'][int(option) - 1]['url']
  title = json['items'][int(option) - 1]['title']
  author = json['items'][int(option) - 1]['uploaderName']
  return functions.addVideos(videoid, title, author), searchVideos()