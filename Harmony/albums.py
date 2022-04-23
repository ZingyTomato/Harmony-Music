import requests
import json
import re
from termcolor import colored
import functions

def searchAlbums():
  album = input(colored("\nAdd albums to the Queue ", 'cyan', attrs=['bold']) + colored("(P)lay, (S)how Queue, (B)ack, (Q)uit: ", 'red'))

  if re.match(functions.URL_REGEX, album):
    return functions.albumLink(), searchAlbums()

  elif re.match(functions.PLAYLIST_REGEX, album):
    return functions.playlistLink(), searchAlbums()

  if album.isnumeric() == True:
    return functions.invalidInput(), searchAlbums()
    
  elif album == "q" or album == "Q":
    return functions.exitProgram()

  elif album == "b" or album == "B" or album == "back" or album == "Back":
    return functions.emptyQueue(), functions.chooseOption()
      
  elif album == "p" or album == "P":
    return functions.playTracks(functions.item_list, functions.queue_list), functions.emptyQueue(), searchAlbums()
      
  elif album == "s" or album == "S":
    return functions.showQueue(functions.item_list), searchAlbums()
      
  return listAlbums(album)
  
def listAlbums(album):
  search_results = functions.getAlbums(album)
  
  if re.match(functions.URL_REGEX, album):
    return functions.albumLink(), searchPlaylists()
  
  if len(search_results['items']) == 0:
    return functions.noResults(album), searchAlbums()
    
  return functions.showResultsAlbumsPlaylists(album, search_results), pickAlbum(search_results, album)

def pickAlbum(json, album):
  item_length = len(json['items'])
  option = input(colored("\nPick an option", 'cyan', attrs=['bold']) + colored(f" [1:{item_length}, (B)ack, (Q)uit]: ", 'red'))

  if option.isnumeric() == False and option != "b" and option != "B" and option != "q" and option != "Q":
    return functions.invalidInput(), pickAlbum(json, album)
    
  elif option == "b" or option == "B":
    return searchAlbums()

  elif option == "q" or option == "Q":
    return functions.exitProgram()

  if int(option) > item_length or int(option) < 1:
    return functions.invalidRange(), pickAlbum(json, album)

  videoid = json['items'][int(option) - 1]['url']
  title = colored(json['items'][int(option) - 1]['name'], 'red')
  author = colored(json['items'][int(option) - 1]['uploaderName'], 'cyan')
  return functions.addItems(videoid, title, author), searchAlbums()