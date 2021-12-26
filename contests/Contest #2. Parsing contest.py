import speech_recognition as sr
import textract as txtrecg
from docx2python import docx2python
import requests
import re
import sphinxbase
import pocketsphinx
from bs4 import BeautifulSoup
# from webdriver_manager.firefox import GeckoDriverManager
from urllib.parse import quote

# driver1 = webdriver.Firefox(executable_path=GeckoDriverManager().install())
# driver1.quit()

def tessractReader(filename):
    text = txtrecg.process(filename)
    return text

def parseDocx(FilePath):
    try:
        return docx2python(FilePath).text
    except:
        print("docx2python can't read the file"+FilePath)


def parseAudio(FilePath):
    r = sr.Recognizer()
    with sr.AudioFile(FilePath) as source:
        audio = r.record(source)  # read the entire audio file

    HOUNDIFY_CLIENT_ID = "_zKZ0JMcRnaaEDDa51O32Q=="  # Houndify client IDs are Base64-encoded strings
    HOUNDIFY_CLIENT_KEY = "xbu-7X143_f4T1S0n97-UAXtbdleAf2O-eYwAnic6Y17ojpAm2Pe84qXKeCldbs6WHJItAdNYIdaPb4Zi-4Y8g=="  # Houndify client keys are Base64-encoded strings
    try:
#         print("Houndify thinks you said " + r.recognize_houndify(audio, client_id=HOUNDIFY_CLIENT_ID, client_key=HOUNDIFY_CLIENT_KEY))
        return(r.recognize_houndify(audio, client_id=HOUNDIFY_CLIENT_ID, client_key=HOUNDIFY_CLIENT_KEY))
    except sr.UnknownValueError:
        print("Houndify could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Houndify service; {0}".format(e))
        

def main():
    
    audiocheck = 0
    texts = ""
    loot = ""
    with open('input.txt', 'r') as fin:
        url = fin.read()
    
    url = url.strip()
    try:
        if "html" in url:
            r=requests.get(url)
            soup=BeautifulSoup(r.content)
            texts = soup.get_text()
        elif "doc" in url:
            r = requests.get(url.strip(), stream=True)
            filename = quote(url.strip(), safe="")
            
            with open(filename, 'wb') as f:
                f.write(r.content)
            f.close()
            
            texts = str(parseDocx(filename)).replace('\\n', '\n').replace('\\r', '').replace('\\t', '')
        elif ".wav" in url:
            r = requests.get(url, stream=True)
            filename = quote(url, safe="")

            with open(filename, 'wb') as f:
                f.write(r.content)
            f.close()

            texts = parseAudio(filename)
            
            audiocheck = 1
        else:
            r = requests.get(url.strip(), stream=True)
            filename = quote(url.strip(), safe="")
            
            with open(filename, 'wb') as f:
                f.write(r.content)
            f.close()
            
            texts = str(tessractReader(filename)).replace('\\n', '\n').replace('\\r', '').replace('\\t', '')
            
    except:
        if ".wav" in url:
            r = requests.get(url, stream=True)
            filename = quote(url, safe="")

            with open(filename, 'wb') as f:
                f.write(r.content)
            f.close()

            texts = parseAudio(filename)
            
            audiocheck = 1
#             text=parseAudio(url) #.replace('\\n', '\n').replace('\\r', '').split('\n')
#         if "docx" in url:
#             text=parseDocx(url) #.replace('\\n', '\n').replace('\\r', '').split('\n')
    if audiocheck == 0:
        regex = re.compile("L(O|0)(O|0)T:(.)*")
        res = regex.search(str(texts))
        if res:
            loot = res.group(0)[5:]
    else:
        loot = str(texts)
        
    with open('output.txt', 'w') as fout:
        fout.write(str(loot))

if __name__ == "__main__":
    main()
