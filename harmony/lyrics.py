import requests
import json
import functions

headers = {
  'authorization': 'Bearer eyJraWQiOiJ2OU1GbFhqWSIsImFsZyI6IkVTMjU2In0.eyJ0eXBlIjoibzJfYWNjZXNzIiwidWlkIjoxODY5NDM0NDcsInNjb3BlIjoicl91c3Igd191c3IiLCJnVmVyIjowLCJzVmVyIjowLCJjaWQiOjIzMTAsImN1ayI6ImFiZDQzMzFmLWU4N2MtNDVhYS05OWUxLTQwNWRkNmRhNThkNyIsImV4cCI6MTY1NDQ5MDY5Nywic2lkIjoiY2ZlZDhkNzYtYmY3My00ZjU5LWIyNzQtOGRjM2ZmZjlkYWQ3IiwiaXNzIjoiaHR0cHM6Ly9hdXRoLnRpZGFsLmNvbS92MSJ9.9z3rYDKmPi2cUi3_FgcgnsFXCOaK2t1SYfKlwk2nbFU2fdbjaixdKlLzAZRAxnZVKnFX9hsrQGaUjT8Tx3SMvw',
  'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.78 Safari/537.36'
}

def searchLyrics(query):
    url = f"https://listen.tidal.com/v1/search/top-hits?query={query}&limit=1&offset=0&types=TRACKS&includeContributors=true&countryCode=US&locale=en_US&deviceType=BROWSER"

    response = requests.request("GET", url, headers=headers).text.encode()

    result = json.loads(response)

    track_id = result['tracks']['items'][0]['id']

    return getLyrics(track_id)

def getLyrics(trackid):
    
    url = f"https://listen.tidal.com/v1/tracks/{trackid}/lyrics?countryCode=US&locale=en_US&deviceType=BROWSER"

    try:
      response = requests.request("GET", url, headers=headers).text.encode()
  
      result = json.loads(response)

      data = result['subtitles'].split("\n")

      dataList = result["subtitles"].split("\n")
      dataDict1 = {line[:10]: line[10:] for line in dataList}
    except:
      functions.SUB_FILE = ""
      return
    return lyricsToVtt(dataDict1)

def lyricsToVtt(data):
    with open("subs.vtt", "w") as file:
        file.write("WEBVTT")
        file.write("\n")
        for (start, text), end in zip(data.items(), list(data.keys())[1:] + [1]):
          try:
            functions.SUB_FILE = "--sub-file=subs.vtt"
            file.write("\n")
            file.write(f"{str(start).strip('[]')} --> {str(end).strip('[]')}\n♪{text} ♪ \n")
          except IndexError:
            return