# from bs4 import BeautifulSoup
from requests_html import HTMLSession
import json
from dotenv import load_dotenv
import os
from pymongo import MongoClient
import api_server.app as app
from api_server.textrank import Summariser

load_dotenv()
client = MongoClient(os.environ.get("MONGO_URL"))
infoDB, infoCollection = None, None
try:
    infoDB = client['info-db']
    infoCollection = infoDB['info-collection']
except:
    print("cannot connect to DB")


class Website:
    def __init__(self, url):
        self.url = url 
        self.title = None
        self.summary = None
        self.paragraphs = None
        self.links = None
        self.saved = False
        # try to retrieve info from database
        info = None
        if(infoCollection != None): info = infoCollection.find_one({'url':self.url})
        if(info and False): 
            self.saved = True
            self.title = info['title']
            self.url = info['url']
            self.summary = info['summary']
            self.links = info['links']
            self.paragraphs = info['paragraphs']
            return
        self.html = self.render()
        for x in self.getKeywords():
            print(x)
        print('eh')
    def getURL(self):
        return self.url

    def getKeywords(self):
        self.text = '\n'.join([x.text for x in self.html.find('p')])
        textrank_keywords = [Summariser.clean_keyword(x) for x in Summariser(self.text).keywords()]
        link_keywords = [Summariser.clean_keyword(x.text) for x in self.html.find('a')]
        all_keywords = Summariser.remove_duplicates(textrank_keywords)
        return [x for x in all_keywords if x != '']
    def getTitle(self): 
        if(self.title == None):
            try:
                self.title = self.html.find('title')[0].text
            except:
                self.title = f"title for {self.url}"
        return self.title
    def getSummary(self): 
        if(self.summary == None):
            try:
                attempts = 0
                while(attempts < 30): 
                    try: self.summary = self.html.find('p')[attempts].text
                    except: self.summary = super().getSummary()
                    attempts += 1
                    if(len(self.summary) > 100): return self.summary
                self.summary = f"summary for {self.url}"
            except:
                self.summary = f"summary for {self.url}"
        return self.summary
    def getJSON(self):
        return {'title': self.getTitle(),
             'url': self.getURL(),
             'summary': self.getSummary()}
    def getJSONString(self):
        info = self.getJSON()
        return json.dumps(info)

    def render(self):
        session = HTMLSession()
        response = session.get(self.url)
        return response.html
class Youtube(Website):
    @classmethod
    def extract_data_from_snippet(cls, snippet, url):
        return {
            'title': snippet['title'],
            'url': url,
            'summary': snippet['description']
        }
    def __init__(self, url):
        self.apiKey : str = os.environ.get('YOUTUBE_API_KEY')
        if('youtube.com/watch?v=' in url):
            self.video_id : str = url.split('?v=')[1].split('&')[0].replace('&','')
        elif('youtu.be' in url):
            self.video_id : str = url.split('/')[-1]
        app.app.logger.info(self.video_id)
        super().__init__(url)
    def getJSON(self):
        query = f"https://www.googleapis.com/youtube/v3/videos?"+\
                f"id={self.video_id}&key={self.apiKey}&part=snippet"
        app.app.logger.info(query)
        session = HTMLSession()
        response = session.get(query)
        snippet = (json.loads(response.text)['items'][0]['snippet'])
        return Youtube.extract_data_from_snippet(snippet, self.url)
    def getJSONString(self):
        info = self.getJSON()
        return json.dumps(info)
class YoutubePlaylist(Website):
    def __init__(self, url):
        self.apiKey : str = os.environ.get('YOUTUBE_API_KEY')
        if('youtube.com/playlist' in url):
            self.playlist_id : str = url.split('list=')[1].split('&')[0].replace('&','')
        super().__init__(url)
    def getJSON(self):
        orig_query = f"https://www.googleapis.com/youtube/v3/playlistItems?"+\
                f"part=snippet&key={self.apiKey}&maxResults=5&playlistId={self.playlist_id}"
        query = orig_query
        done = False
        video_ids = []
        page_token = None
        while(not done):
            session = HTMLSession()
            if page_token is not None:
                query = orig_query + f"&pageToken={page_token}"
            response = session.get(query)
            data = json.loads(response.text)
            rpp = int(data['pageInfo']['resultsPerPage'])
            tr = int(data['pageInfo']['totalResults'])
            for i in data['items']:
                video_ids.append(
                    Youtube.extract_data_from_snippet( i['snippet'], 
                    f"https://youtu.be/{i['snippet']['resourceId']['videoId']}")
                )
            if(rpp < tr and 'nextPageToken' in data):
                page_token = data['nextPageToken']
            else:
                break
        return video_ids
    def getJSONString(self):
        info = self.getJSON()
        return json.dumps(info)

class Wiki(Website):
    def __init__(self, url):
        url = url.split('#')[0]
        super().__init__(url)
        # if unsaved yet
        if(self.saved == False): 
            # save() generates json for the first time
            self.save()
    def save(self):
        self.saved = True
        if(infoCollection != None): infoCollection.insert_one(self.exportToDB())
    def exportToDB(self):
        return {'title': self.getTitle(),
             'url': self.getURL(),
             'summary': self.getSummary(),
             'paragraphs': self.getParagraphs(), 
             'links': self.getLinks() }

    def getTitle(self):
        if(self.title == None): 
            try: self.title = self.html.find('#firstHeading')[0].text
            except: self.title = super().getTitle()
        return self.title
    def getURL(self): 
        return self.url
    def getSummary(self): # 
        if(self.summary == None): 
            attempts = 1
            while(attempts < 10): 
                try: self.summary = self.html.find('p')[attempts].text
                except: self.summary = super().getSummary()
                attempts += 1
                if(len(self.summary) > 100): break
        return self.summary
    def getParagraphs(self):
        if(self.paragraphs == None): 
            self.paragraphs = [i.text for i in self.html.find('p')]
        return self.paragraphs
    def getLinks(self):
        if(self.links == None):
            self.links = list(self.html.absolute_links)
        return self.links
    def getJSON(self):
        return {'title': self.getTitle(),
             'url': self.getURL(),
             'summary': self.getSummary()}
    def getJSONString(self):
        info = self.getJSON()
        return json.dumps(info)

class ArXiv(Website):
    def __init__(self, url):
        url = url.replace('.pdf', '')
        self.url = url
        self.authors = None
        super().__init__(url)
        if(self.saved == False):
            self.save()
    def getTitle(self):
        if(self.title == None): 
            self.title = self.html.find('title')[0].text.split('\n')[0]
        return self.title
    def getAuthors(self):
        if(self.authors == None): 
            self.authors = self.html.find('.authors')[0].text.split('\n')[0].replace('Authors:','').split(',')
        return self.authors
    def getAbstract(self):
        return self.html.find('.abstract')[0].text.split('\n')[0]
    def getSummary(self): # summary is just abstract
        if(self.summary == None): 
            self.summary = self.getAbstract()
        return self.summary
    def getURL(self):
        return self.url
    def save(self):
        return 
    def getJSONString(self):
        return {'title': self.getTitle(),
             'url': self.getURL(),
             'summary': self.getSummary()}

class Medium(Website):
    def __init__(self, url):
        url = url.split('#')[0]
        super().__init__(url)
        # if unsaved yet
        if(self.saved == False): 
            # save() generates json for the first time
            self.save()
    def save(self):
        self.saved = True
        if(infoCollection != None): infoCollection.insert_one(self.exportToDB())
    def exportToDB(self):
        return {'title': self.getTitle(),
             'url': self.getURL(),
             'summary': self.getSummary(),
             'paragraphs': self.getParagraphs(), 
             'links': self.getLinks() }

    def getTitle(self):
        if(self.title == None): 
            try: self.title = self.html.find('.pw-post-title')[0].text
            except: self.title = super().getTitle()
        return self.title
    def getURL(self): 
        return self.url
    def getSummary(self): # 
        if(self.summary == None): 
            attempts = 0
            while(attempts < 10): 
                try: self.summary = self.html.find('.pw-post-body-paragraph')[attempts].text
                except: self.summary = super().getSummary()
                attempts += 1
                if(len(self.summary) > 100): break
        return self.summary
    def getParagraphs(self):
        if(self.paragraphs == None): 
            self.paragraphs = [i.text for i in self.html.find('p')]
        return self.paragraphs
    def getLinks(self):
        if(self.links == None):
            self.links = list(self.html.absolute_links)
        return self.links
    def getJSON(self):
        return {'title': self.getTitle(),
             'url': self.getURL(),
             'summary': self.getSummary()}
    def getJSONString(self):
        info = self.getJSON()
        return json.dumps(info)

class Edge:
    def __init__(self, A, B):
        self.A = A
        self.B = B
class Node:
    def __init__(self, url):
        self.url = url
        self.obj = None
        self.edgesOut = []
        self.edgesIn = []
        if('en.wikipedia.org' in self.url): self.obj = Wiki(self.url)
    def addEdge(self, B):
        self.edgesOut.append(Edge(self,B))
        self.edgesIn.append(Edge(B,self))
class WikiCrawler:
    def __init__(self):
        self.nodes = []
        self.queue = []
    def stepBFS(self, node = None):
        if(node == None): node = self.queue[0]
        if(node in self.queue): self.queue.remove(node)
        if(node.obj == None): return
        print(f'bfs @ {node.url}')
        for nextLink in node.obj.links:
            next = Node(nextLink)
            node.addEdge(next)
            self.nodes.append(next)
            self.queue.append(next)
if(__name__ == "__main__"):
    pass
    # wc = WikiCrawler()
    # wc.stepBFS(Node('https://en.wikipedia.org/wiki/Quantum_field_theory'))

    # for i in range(10):
    #     wc.stepBFS()