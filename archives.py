
# coding: utf-8

# In[129]:


from bs4 import BeautifulSoup as bs
import urllib
import requests
import os
from datetime import datetime 
from datetime import timedelta 
import re
from DB import DB

def getfiles(path):
    return [file for file in os.listdir(path) if os.path.isfile(os.path.join(path,file))]

GLOBAL_BASE_URL = 'https://www.dawn.com/archive/'
GLOBAL_HEADERS=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]

def write_to_file(name, data):
    print(name)
    with open('DATA/' + name , 'w') as outfile:
        outfile.write(data)

def normalize_uri(uri):
    return uri.replace('/', '_',)

def R(uri, data=None, base_url=GLOBAL_BASE_URL, headers=GLOBAL_HEADERS):
    return requests.get(base_url + uri, data)

existing_files = getfiles('./DATA')




def run():
    
    db = DB(username='', password='', selected_db='news')
    
    i = 2947
    date_now = datetime.now() 
    
    
    tries = 0
    
    while i > 0:  
        
        dt = date_now-timedelta(days=i)
        uri = dt.strftime("%Y-%m-%d")
        print('date = ', uri)
        
        col = db.findOrCreateCollection('archives_links')
        skiped = db.findOrCreateCollection('skiped_links')
        
        try:
            page = R(uri)
            
            html = bs(page.content, 'lxml')
            print('length of HTML: ', len(str(page.content)))
            if (len(str(page.content)) < 1000):
                if tries < 3:
                    print('Excetion: Content too short, ', (len(str(page.content)), 'Try: ', tries))
                    tries += 1
                    continue
                tries = 0
                
                doc = skiped.createDocument({
                    'uri': GLOBAL_BASE_URL + uri,
                    'date': uri
                })
                doc.save()
                i -= 1
                continue
            
            try:
                ahrefs = html.findAll('a')
            except Exception as e:
                print('Excpetion: Can not find links on page: Length of document is: ',  len(str(html.body)), e)
            document_links = set()

            for href in ahrefs:
                try:
                    if (re.match(r'^(https://www\.dawn\.com/news).*', href['href'])):
                        document_links.add(href['href'])
                    else:
                        #print(href['href'])
                        pass
                    
                except Exception as e:
                    print('Exception: ', e, ' -- skipping ', href)
            
            if len(document_links) < 1 and tries < 3:
                tries += 1
                continue
            print('Documents saving!', len(document_links))
            doc = col.createDocument({'stories': list(document_links), 'date': uri})
            doc.save()
            
            tries = 0
            
        except Exception as e:
            print('Exception:', e)
            if tries < 3:
                print('trying again: ', uri, tries)
                tries += 1
                continue
            tries = 0
        i -= 1
run()
print('done!')


# In[136]:



(datetime.now() - datetime(2009,10,1)).days



