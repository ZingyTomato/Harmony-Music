import requests
import json
import re
from termcolor import colored
import functions

def searchSongs():

  song = input(colored("\nAdd songs to the Queue ", 'cyan', attrs=['bold']) + colored("(P)lay, (S)how Queue, (Q)uit: ", 'red'))

  if re.match(functions.YOUTUBE_REGEX, song):
    return functions.youtubeLink(song)

  elif re.match(functions.URL_REGEX, song):
    return functions.urlLink(song)

  if song.isnumeric() == True:
    return functions.invalidInput(), searchSongs()
    
  elif song == "q" or song == "Q":
    return functions.exitProgram()
      
  elif song == "p" or song == "P":
    return functions.playTracks()
      
  elif song == "s" or song == "S":
    return functions.showQueue()
      
  return listTracks(song)
  
def listTracks(song):
  
  if re.match(functions.YOUTUBE_REGEX, song):
    return functions.youtubeLink(song)

  elif re.match(functions.URL_REGEX, song):
    return functions.urlLink(song)
    
  return functions.getSongs(song)

def pickTrack(song, json):

  item_length = len(json['results'])
  
  option = input(colored("\nPick an option", 'cyan', attrs=['bold']) + colored(f" [1:{item_length}, (B)ack, (Q)uit]: ", 'red'))

  if option.isnumeric() == False and option != "b" and option != "B" and option != "q" and option != "Q":
    return functions.invalidInput(), pickTrack(song, json)
    
  elif option == "b" or option == "B":
    return searchSongs()

  elif option == "q" or option == "Q":
    return functions.exitProgram()

  if int(option) > item_length or int(option) < 1:
    return functions.invalidRange(), pickTrack(song, json)

  videoid = json['results'][int(option) - 1]['downloadUrl'][4]['link']
  title = json['results'][int(option) - 1]['name']
  author = json['results'][int(option) - 1]['artist']
  return functions.addSongs(videoid, title, author)
