import requests
import json
import functions
import time

headers = {
  'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.78 Safari/537.36'
}

def parseTime(s):
    return time.strftime('%H:%M:%S.%MS',time.gmtime(s))

def searchLyrics(query):
    try:
      data = requests.request("GET", f"{functions.LYRICS_API}/lyrics?q={functions.fixFormatting(query)}", headers=headers).text.encode()
      data = json.loads(data)
      functions.SUB_FILE = "--sub-file=subs.vtt"
    except:
      functions.SUB_FILE = ""
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
