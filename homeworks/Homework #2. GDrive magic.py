#!/usr/bin/env python
# coding: utf-8

# # Part 1. Authentication in a service

# ## 1.1. What do you store in your Google Drive?
# 
# Sometimes it can be quite troublesome to crawl web data - for example, when you can't just collect data from web-pages because the authentification to a website is required. Today's tutorial is about a dataset of special type - namely, Google Drive data. You will need to get access to the system using OAuth protocol, download and parse files of different types.
# 
# Plan. 
# 1. Download [this little archive](https://drive.google.com/open?id=1Xji4A_dEAm_ycnO0Eq6vxj7ThcqZyJZR), **unzip** it and place the folder anywhere inside your Google Drive. You should get a subtree of 6 folders with files of different types: presentations, pdf-files, texts, and even code.
# 2. Go to [Google Drive API](https://developers.google.com/drive/api/v3/quickstart/python) documentation, read [intro](https://developers.google.com/drive/api/v3/about-sdk) and learn how to [search for files](https://developers.google.com/drive/api/v3/reference/files/list) and [download](https://developers.google.com/drive/api/v3/manage-downloads) them. Pay attention, that  working at `localhost` (jupyter) and at `google colab` can be slighty different. We expect you to run from localhost.
# 3. Learn how to open from python such files as [pptx](https://python-pptx.readthedocs.io/en/latest/user/quickstart.html), pdf, docx or even use generalized libraries like [textract](https://textract.readthedocs.io/en/stable/index.html), save internal text in a file near.
# 4. Write a code with returns names (with paths) of files for a given substring. Test on these queries.
# ```
# segmentation
# algorithm
# classifer
# printf
# predecessor
# Шеннон
# Huffman
# function
# constructor
# machine learning
# dataset
# Протасов
# Protasov
# ```

# ### 1.1.1. Access GDrive ###
# 
# Below is the example of how you can oranize your code - it's fine if you change it.
# 
# Let's extract the list of all files that are contained (recursively) in t
# he folder of interest. In my case, I called it `air_oauth_folder`.

# In[202]:


# install some dependencies
get_ipython().system('pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib')
# !pip install --upgrade six


# In[1]:


from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from googleapiclient.http import MediaIoBaseDownload

"""Shows basic usage of the Drive v3 API.
Prints the names and ids of the first 10 files the user has access to.
"""

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

config = {"installed":{"client_id":"235774715710-tah0thbhuv9frlm8hqg4rjgrr7q8b0t4.apps.googleusercontent.com","project_id":"assignment2-1611750152663","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"0g0RD33YKPxevVp0U3LJ33K1","redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]}}
creds = None

flow = InstalledAppFlow.from_client_config(
            config, SCOPES)
creds = flow.run_local_server(port=0)

drive_service = build('drive', 'v3', credentials=creds)

def gdrive_get_all_files_in_folder(folder_name):
    #TODO retrieve all files from a given folder
    listofFiles = []

    page_token = None
    while True:
        response = drive_service.files().list(q="name = '"+folder_name+"'",
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
                                              pageToken=page_token).execute()

        for file in response.get('files', []):               
                file_id = file.get('id')
                results = drive_service.files().list(q = "'" + file_id + "' in parents", 
                                                     spaces='drive',
                                                  fields='nextPageToken, files(id, name)',
                                                  pageToken=page_token).execute()
                items = results.get('files', [])
                i = len(items)
                while items != []:
                    ob1 = items.pop()
                    if "." in ob1['name']:
                        listofFiles.append([ob1['id'], ob1['name']])
                    else:
                        results2 = drive_service.files().list(q = "'" + ob1['id'] + "' in parents", 
                                                             spaces='drive',
                                                             fields='nextPageToken, files(id, name)',
                                                             pageToken=page_token).execute()
                        items2 = results2.get('files', [])
                        items.extend(items2)

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return listofFiles

def gdrive_download_file(file, path_to_save): 
    #TODO download file and save it under the path
#     print(file)
    file_id = file[0] 
    filename = str(path_to_save) +"/"+ str(file[1])
    
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)
    
    request = drive_service.files().get_media(fileId=file_id)

    fh = io.FileIO(filename, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while done is False:
        status, done = downloader.next_chunk()
#         print ("Download %d%%." % int(status.progress() * 100))
    pass


# In[2]:


folder_of_interest = 'data11'
files = gdrive_get_all_files_in_folder(folder_of_interest)

test_dir = "test_files2"
for item in files:
    gdrive_download_file(item, test_dir)


# ### 1.1.2. Tests ###
# Please fill free to change function signatures and behaviour.

# In[3]:


assert len(files) == 34, 'Number of files is incorrect'
print('n_files:', len(files))

print("file here means id and name, e.g.: ", files[0])

gdrive_download_file(files[0], '.')

import os.path
assert os.path.isfile(os.path.join('.', files[0][1])), "File is not downloaded correctly"


# ## 1.2. Read files content
# ### 1.2.1. Read

# In[153]:


# install dependencies
get_ipython().system('pip install textract')
get_ipython().system('pip install pydub')
get_ipython().system('pip install moviepy')

import os
# cmd1 = "apt -qq install -y sox" # If there is a sox error, kindly run this command in os.popen
command = "apt-get -y install ffmpeg"
os.popen("sudo -S %s"%(command), 'w').write('your_system_password') # please put your password here to install this library


# For windows please refer to 
# - https://textract.readthedocs.io/en/latest/installation.html#don-t-see-your-operating-system-installation-instructions-here
# 
# - https://www.xpdfreader.com/download.html
# 
# ALSO BE CAREFUL WITH SPACES IN NAMES. Better save without spaces!!!!

# In[1]:


import textract
import speech_recognition as sr
import io
from bs4 import BeautifulSoup
import sys

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from pydub import AudioSegment # uses FFMPEG
from moviepy.editor import *

def pdfparser(data):

    fp = open(data, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.

    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        data =  retstr.getvalue()

#     print(data)
    if "ﬁ" in data:
        data = data.replace("ﬁ", "fi")
    return data



def processAudio(filepath, chunksize=60000):
    #0: load mp3
    sound = AudioSegment.from_mp3(filepath)
    
    path = filepath[:-3]
    

    #1: spliting the file into 60s chunks
    def divide_chunks(sound, chunksize):
        # looping till length l
        for i in range(0, len(sound), chunksize):
            yield sound[i:i + chunksize]
    chunks = list(divide_chunks(sound, chunksize))
#     print(f"{len(chunks)} chunks of {chunksize/1000}s each")

    r = sr.Recognizer()
    #2: per chunk, save to wav, then read and run through recognize_google()
    string_index = {}
    i=0
    textfromaudio = ""
    for index,chunk in enumerate(chunks):
        #TODO io.BytesIO()
        
        
        chunk.export(path+'1.wav', format='wav')
        with sr.AudioFile(path+'1.wav') as source:
            audio = r.record(source)
        
        s = ""
#         s = textract.process(path+'1.wav', lang='rus')
        
        os.remove(path+'1.wav')
        try:
            s = r.recognize_google(audio, language='ru-RU')
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google service; {0}".format(e))

        textfromaudio += " " + str(s)
        """
        the audio is lengthy, this check is for saving the time, 
        if you want to transcribe the whole audio just comment this check
        """
        i += 1
        if i == 1: 
            break
    
    return textfromaudio


def get_file_strings(path):
    #TODO change this function to handle different data types properly 
    # - textract is not able to parse everything
    # Take care of non-text data too
    texts = ""
    if ".mp3" in path:
        texts = ""
#         print("audio"+path)
#         texts = str(processAudio(path))
    elif "avi" in path:
        texts = ""
#         videoclip = VideoFileClip(path)
#         audioclip = videoclip.audio

#         if audioclip == None:
#             texts = ""
#         else:
#             try:
#                 texts = r.recognize_google(audioclip)
#             except sr.UnknownValueError:
#                 texts = ""
#                 print("Could not understand audio")
#             except sr.RequestError as e:
#                 texts = ""
#                 print("Could not request results from Google service; {0}".format(e))
    elif ".cpp" in path:
        soup=BeautifulSoup(open(path), 'lxml')
        texts = soup.get_text()
    elif ".c" in path:
        soup=BeautifulSoup(open(path), 'lxml')
        texts = soup.get_text()
    elif ".js" in path:
        soup=BeautifulSoup(open(path), 'lxml')
        texts = soup.get_text()
    elif ".html" in path:
        soup=BeautifulSoup(open(path), "html.parser")
        texts = soup.get_text()
        
    elif ".pdf" in path:
        texts = pdfparser(path)
    elif ".txt" in path:
        try:
            f = open(path, encoding='utf-8', mode='r')
            text = f.read()
        except UnicodeDecodeError:
            f = open(path, "r", encoding = "ISO-8859-1")
            text = f.read()
        texts = str(text)
    else:
        try:
            text = textract.process(path)
        except UnicodeDecodeError:
            f = open(path, "r", encoding = "ISO-8859-1")
            text =f.read()

        texts = str(text)
    if texts == "":
#         print(path)
        return None
    else:
#         print(len(texts))
        texts = str(texts).replace('\\n', '\n').replace('\\r', '').split('\n')

    return str(texts)


# In[3]:


# creating dictionary of parsed files
test_dir = "test_files2"
files_data = dict()
for file in os.scandir(test_dir):
    strings = get_file_strings(file.path)
    if strings:
        files_data[file.name] = strings


# ### 1.2.2. Tests for read

# In[4]:


assert len(files_data) == 31 # there should be 33 files
print(len(files_data))

assert "Protasov" in get_file_strings(os.path.join(test_dir, 'at least this file.txt')), "TXT File parsed incorrectly"
assert "A. Image classification" in get_file_strings(os.path.join(test_dir, 'deep-features-scene (1).pdf')), "PDF File parsed incorrectly"


# ## 1.3. Tests

# In[41]:


def find(query):
    #TODO implement search procedure
    ret = []
    notfound = ["Couldn't", "Find"]
    for key in files_data:
        ele = files_data[key]
        if isinstance(ele, dict):
            for k, v in ele.items():
                text = v.lower()
                if query.lower() in text:
                    slideId = "Presentation: "+str(key) + ", Slide No: "+ str(k)
                    ret.append(slideId)
        else:
            text = ele.lower()
            if query.lower() in text:
                ret.append(key)
    if len(ret) <= 1:
        ret.extend(notfound)
    return ret


# In[30]:


queries = ["segmentation", "algorithm", "printf", "predecessor", "Huffman",
           "function", "constructor", "machine learning", "dataset", "Protasov"]

for query in queries:
    r = find(query)
#     print("Results for: ", query)
#     print("\t", r)
    assert len(r) > 0, "Query should return at least 1 document"
    assert len(r) > 1, "Query should return at least 2 documents"
    assert "at least this file.txt" in r, "This file has all the queries. It should be in a result"


# # 2. Parse me if you can #
# 
# Sometimes when crawling we have to parse websites that turn out to be SaaS - i.e., there is a special JS application which renders documents and which is downloaded first. Therefore, data that is to be rendered initially comes in a proprietary format. One of the examples is Google Drive. Last time we downladed and parsed some files from GDrive, however, we didn't parse GDrive-specific file formats, such as google sheets or google slides.
# 
# Today we will learn to obtain and parse such data using Selenium - a special framework for testing web-applications.
# 
# ## 2.1. Getting started
# 
# Let's try to load and parse the page the way we did before:

# In[159]:


import requests
from bs4 import BeautifulSoup
resp = requests.get("https://docs.google.com/presentation/d/1LuZvz3axBD8UuHLagdv0EbhsGEWJmpd7gN5KjwYCp9Y/edit?usp=sharing")
soup = BeautifulSoup(resp.text, 'lxml')
print(soup.body.text[:1000])


# As we see, the output is not what we expect. So, what can we do when a page is not being loaded right away, but is rather rendered by a script? Browser engines can help us get data. Let's try to load the same web-page, but do it in a different way: let's give some time to a browser to load the scripts and run them; and then will work with DOM (Document Object Model), but will get it from browser engine itself, not from BeautifulSoup.
# 
# Where do we get browser engine from? Simply installing a browser will do the thing. How do we send commands to it from code and retrieve DOM? Service applications called drivers will interpret out commands and translate them into browser actions.
# 
# 
# For each browser engine suport you will need to:
# 1. install browser itself;
# 2. download 'driver' - binary executable, which passed commands from selenium to browser. E.g. [Gecko == Firefox](https://github.com/mozilla/geckodriver/releases), [ChromeDriver](http://chromedriver.storage.googleapis.com/index.html);
# 3. unpack driver into a folder under PATH environment variable. Or specify exact binary location.
# 
# ### 2.1.1. Download driver
# 
# And place it in any folder or under PATH env. variable.
# 
# ### 2.1.2. Install selenium

# In[160]:


get_ipython().system('pip install -U selenium')
import os
command = "apt install firefox-geckodriver"
os.popen("sudo -S %s"%(command), 'w').write('your_password') # please put your password here to install this library


# In[7]:


from selenium import webdriver


# ### 2.1.3. Launch browser
# 
# This will open browser window

# In[162]:


browser = webdriver.Firefox()
# or explicitly
# browser = webdriver.Firefox(
#     executable_path='geckodriver', 
#     firefox_binary='C:/Program Files/Mozilla Firefox/firefox.exe'
# )


# ### 2.1.4. Download the page
# 

# In[163]:


# navigate to page
browser.get('http://tiny.cc/00dhkz')
browser.implicitly_wait(5)  # wait 5 seconds

# select all text parts from document
elements = browser.find_elements_by_css_selector("g.sketchy-text-content-text")
# note that if number differs from launch to launch this means better extend wait time
print("Elements found:", len(elements))

# oh no! It glues all the words!
print("What if just a silly approach:", elements[0].text)

# GDrive stores all text blocks word-by-word
subnodes = elements[0].find_elements_by_css_selector("text")
text = " ".join(n.text for n in subnodes)
print("What if a smart approach:", text)


# In[164]:


browser.quit()


# - Too slow, wait for browser to open, browser to render
# 
# ## 2.2. Headless
# 
# Browsers (at least [FF](https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Headless_mode), [Chrome](https://intoli.com/blog/running-selenium-with-headless-chrome/), IE) have headless mode - no window rendering and so on. Means it should work much faster!

# In[165]:


options = webdriver.FirefoxOptions()

options.add_argument('-headless')
options.add_argument('window-size=1200x600')
browser = webdriver.Firefox(options=options)


# In[166]:


## SAME CODE

# navigate to page
browser.get('http://tiny.cc/00dhkz')
browser.implicitly_wait(5)  # wait 5 seconds

# select all text parts from document
elements = browser.find_elements_by_css_selector("g.sketchy-text-content-text")
# note that if number differs from launch to launch this means better extend wait time
print("Elements found:", len(elements))

# oh no! It adds NEW LINE. Behavior differs!!!!
print("What if just a silly approach:", elements[0].text)

# GDrive stores all text blocks word-by-word
subnodes = elements[0].find_elements_by_css_selector("text")
text = " ".join(n.text for n in subnodes)
print("What if a smart approach:", text)


# In[167]:


browser.quit()


# ### 2.2.1. NB 
# Note, that browser behavior differs for the same code!
# 
# ## 2.3. Task 
# Our lectures usually have lot's of links. Here are the links to original (spring 2020) versions of the documents.
# 
# [4. Vector space](https://docs.google.com/presentation/d/1UxjGZPPrPTM_3lCa_gWTk8yZI_qNmTKwtMxr8JZQCIc/edit?usp=sharing)
# 
# [6. search trees](https://docs.google.com/presentation/d/1LuZvz3axBD8UuHLagdv0EbhsGEWJmpd7gN5KjwYCp9Y/edit?usp=sharing)
# 
# [7-8. Web basics](https://docs.google.com/presentation/d/1bgsCgpjMcQmrFpblRI6oH9SnG4bjyo5SzSSdKxxHNlg/edit?usp=sharing)
# 
# Please complete the following tasks:
# 
# ### 2.3.1. Search for slides with numbers
# I want to type a word, and it should say which slides of which lecture has this word.

# In[37]:


from selenium.webdriver.common.keys import Keys

options = webdriver.FirefoxOptions()

options.add_argument('-headless')
options.add_argument('window-size=1200x600')

def getTextAndImgsFromSlides(url):    
    slides_text = dict() # dictionary slide_num : slide_text
    img_list = [] # list of image urls
    slidnum = 1

    #TODO: parse google slides and save all text and image urls in slides_text and img_list
    # you should get the contents from ALL slides - however, you will see that at one moment 
    # of time only single slide + few slide previews on the left are visible. To be able to    
    # reach all slides you will need to scroll to and click these previews. While slide contents 
    # can be obtained from previews themselves, speaker notes (which you also have to extract)
    # can be viewed only if a particular slide is open.
    # to scroll the element of interest into view, use can this: 
    # browser.execute_script("arguments[0].scrollIntoView();", el)
    # to click the element, use can use ActionChains library   
    browser = webdriver.Firefox(options = options)
    browser.get(url)

    browser.find_element_by_css_selector('body').send_keys(Keys.HOME)
    browser.implicitly_wait(15)

    element = browser.find_element_by_class_name("panel-right")

    #First page images are not loaded
    images   = element.find_elements_by_css_selector("image")
    for image in images:
        img_src = image.get_attribute("href")
        img_list.append(img_src)

    subelem = element.find_elements_by_css_selector("svg")
    truncatingelem = []
    browser.implicitly_wait(5)
    title = browser.title

    while subelem !=[]:
        elem = subelem.pop()
        if elem not in truncatingelem:
            if elem.is_displayed():
                truncatingelem.append(elem)
                texts = element.find_elements_by_css_selector("g.sketchy-text-content-text")

                textt = ""
                for text in texts:
                    subnodes = text.find_elements_by_css_selector("text")
                    text = " ".join(n.text for n in subnodes)
                    textt += text
                if len(textt.strip())>1:
                    slides_text[str(slidnum)] = textt
                    slidnum += 1

                images   = elem.find_elements_by_css_selector("image")
                for image in images:
                    img_src = image.get_attribute("href")
                    img_list.append(img_src)

                browser.find_element_by_css_selector('body').send_keys(Keys.DOWN)
                tempsubelem = element.find_elements_by_css_selector("svg")

                # for counting slides
                for tempelem in tempsubelem:
                    if tempelem not in truncatingelem and tempelem not in subelem:
                        subelem.append(tempelem)
    del slides_text[str(len(slides_text))]
    return slides_text, img_list, title


# Parsing three presentations

# In[38]:


links = ["https://docs.google.com/presentation/d/1UxjGZPPrPTM_3lCa_gWTk8yZI_qNmTKwtMxr8JZQCIc/edit?usp=sharing", 
         "https://docs.google.com/presentation/d/1LuZvz3axBD8UuHLagdv0EbhsGEWJmpd7gN5KjwYCp9Y/edit?usp=sharing",
         "https://docs.google.com/presentation/d/1bgsCgpjMcQmrFpblRI6oH9SnG4bjyo5SzSSdKxxHNlg/edit?usp=sharing"]


all_imgs = []
all_texts = dict()

for i, link in enumerate(links):
    texts, imgs, title = getTextAndImgsFromSlides(link)
    all_texts[str(title)] = texts
    files_data[str(title)]=texts 
    all_imgs.append(imgs)


# ### 2.3.2. Tests

# In[39]:


texts, imgs, title = getTextAndImgsFromSlides('http://tiny.cc/00dhkz')

assert len(texts) == 35 # equal to the total number of slides in the presentation 
print(len(texts))

assert len(imgs) > 26 # can be more than that due to visitor icons
print(len(imgs))

assert any("Navigable" in value for value in texts.values()) # word is on a slide
assert any("MINUS" in value for value in texts.values()) # word is in speaker notes


# In[42]:


queries = ["architecture", "algorithm", "function", "dataset", 
           "Protasov", "cosine", "модель", "например"]

for query in queries:
    r = find(query)
    print("Results for: ", query)
    print("\t", r)
    assert len(r) > 0, "Query should return at least 1 document"
    assert len(r) > 1, "Query should return at least 2 documents"


# In[ ]:




