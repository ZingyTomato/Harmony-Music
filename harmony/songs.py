import requests
import json
import re
from termcolor import colored
import functions
import os
import time

def searchSongs():

  song = input(colored("\nAdd songs to the Queue ", 'cyan', attrs=['bold']) + colored("(P)lay, (S)how Queue, (Q)uit: ", 'red'))

  if re.match(functions.YOUTUBE_REGEX, song):
    return functions.youtubeLink(), functions.playTracksURL(song)

  elif re.match(functions.URL_REGEX, song):
    return functions.urlLink(), functions.playTracksURL(song)

  if song.isnumeric() == True:
    return functions.invalidInput(), searchSongs()
    
  if song == "":
    return functions.emptyInput(), searchSongs()

  elif song == "q" or song == "Q":
    return functions.removeSubs(), functions.exitProgram()
      
  elif song == "p" or song == "P":
    return functions.playTracks(), searchSongs()
      
  elif song == "s" or song == "S":
    return functions.showQueue(), searchSongs()
      
  return listTracks(song)
  
def listTracks(song):
  
  if re.match(functions.YOUTUBE_REGEX, song):
    return functions.youtubeLink(), functions.playTracksURL(song)

  elif re.match(functions.URL_REGEX, song):
    return functions.urlLink(), functions.playTracksURL(song)
    
  return functions.getSongs(song)

def pickTrack(song, json):

  item_length = len(json['results'])
  
  option = input(colored("\nPick an option", 'cyan', attrs=['bold']) + colored(f" [1:{item_length}, (B)ack, (Q)uit]: ", 'red'))

  if option.isnumeric() == False and option != "b" and option != "B" and option != "q" and option != "Q":
    return functions.invalidInput(), pickTrack(song, json)
    
  elif option == "b" or option == "B":
    return functions.removeSubs() , searchSongs()

  elif option == "q" or option == "Q":
    return functions.removeSubs(), functions.exitProgram()

  if int(option) > item_length or int(option) < 1:
    return functions.invalidRange(), pickTrack(song, json)

  if json['results'][int(option) - 1]['downloadUrl'] == False:
   return functions.noStreamUrl(), searchSongs()

  videoid = json['results'][int(option) - 1]['downloadUrl'][4]['link']
  title = functions.fixFormatting(json['results'][int(option) - 1]['name'])
  author = functions.fixFormatting(json['results'][int(option) - 1]['primaryArtists'])
  duration = time.strftime('%M:%S',time.gmtime(int(json['results'][int(option) - 1]['duration'])))
  explicit = functions.isExplicit(json['results'][int(option) - 1]['explicitContent'])
  
  return functions.addSongs(videoid, title, author, duration, explicit)