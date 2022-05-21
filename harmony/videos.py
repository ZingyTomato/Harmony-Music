import requests
import json
import re
from termcolor import colored
import functions
import os

def searchVideos():

  video = input(colored("\nAdd videos to the Queue ", 'cyan', attrs=['bold']) + colored("(P)lay, (S)how Queue, (Q)uit: ", 'red'))

  if re.match(functions.YOUTUBE_REGEX, video):
    return functions.youtubeLink(), functions.playVideosURL(video)

  elif re.match(functions.URL_REGEX, video):
    return functions.urlLink(), functions.playVideosURL(video)

  if video.isnumeric() == True:
    return functions.invalidInput(), searchVideos()
    
  if video == "":
    return functions.emptyInput(), searchVideos()

  elif video == "q" or video == "Q":
    return functions.exitProgram()
      
  elif video == "p" or video == "P":
    return functions.playVideos(), searchVideos()
      
  elif video == "s" or video == "S":
    return functions.showQueue(), searchVideos()
      
  return listVideos(video)
  
def listVideos(video):
  
  if re.match(functions.YOUTUBE_REGEX, video):
    return functions.youtubeLink(), functions.playVideosURL(video)

  elif re.match(functions.URL_REGEX, video):
    return functions.urlLink(), functions.playVideosURL(video)
    
  return functions.getVideos(video)

def pickVideo(video, json):

  item_length = len(json['items'])
  
  option = input(colored("\nPick an option", 'cyan', attrs=['bold']) + colored(f" [1:{item_length}, (B)ack, (Q)uit]: ", 'red'))

  if option.isnumeric() == False and option != "b" and option != "B" and option != "q" and option != "Q":
    return functions.invalidInput(), pickVideo(video, json)
    
  elif option == "b" or option == "B":
    return searchVideos()

  elif option == "q" or option == "Q":
    return functions.exitProgram()

  if int(option) > item_length or int(option) < 1:
    return functions.invalidRange(), pickVideo(video, json)

  videoid = json['items'][int(option) - 1]['url']
  title = json['items'][int(option) - 1]['title']
  author = json['items'][int(option) - 1]['uploaderName']
  return functions.addVideos(videoid, title, author)
