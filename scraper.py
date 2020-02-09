import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup , Comment
#import crawler.datastore as data
from crawler.datastore import DataStore
import utils.team_utils as tutils
from urllib.robotparser import RobotFileParser
import redis
#import Levenshtein
import requests
r = redis.Redis(host="localhost",port=6379,db=0)
# Not sure if we should have this. From a yt vid I watched
# https://www.youtube.com/watch?v=dlI-xpQxcuE

#r.set('language', 'Python', px = 10000)


visitedURL="urls"
uniqueUrl = "unique"
blackList = "blackListed"
robotsCheck ="robotsDict"
storeSeeds = 0
repeatedUrl = ['url',0]#If we visit the same url 3 times in a row, add it to blacklist and skip.

def scraper(url, resp):
    global storeSeeds
    if storeSeeds == 0:  # Store seed robot.txts only once.
        tutils.robotsTxtParseSeeds()
        storeSeeds += 1

    links = extract_next_links(url, resp)
    if (links != None):
        return [link for link in links if tutils.isValid(link)]  # automatically adds to frontier
    else:
        return list()

def extract_next_links(url, resp):
    listLinks = list()

    # if Levenshtein.distance(url, tutils.four0four) <= 10:
    #     return
    if(resp.raw_response == None):  #600+ statuses return a None object for resp.raw_response
        r.sadd(blackList, url)
        return

    if (resp.raw_response.status_code > 399 and resp.raw_response.status_code < 600): # should we avoid 400 statuses?
        r.sadd(blackList,url)
        return  #maybe add to blacklist instead of returning

    if (resp.status > 399 and resp.status < 600): # should we avoid 400 statuses?
        r.sadd(blackList,url)
        return  #maybe add to blacklist instead of returning

    if (resp.raw_response.status_code < 199 and resp.raw_response.status_code < 400):
        if (int(resp.raw_response.headers._store["content-length"][1]) > 2000000): #2MB limit
            r.sadd(blackList,url)
            return
        elif (int(resp.raw_response.headers._store["content-length"][1]) < 500): #500 bytes
            r.sadd(blackList,url)
            return

    if tutils.isValid(url):
        r.sadd(visitedURL,url)

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

    for tag in soup(text=lambda text: isinstance(text,Comment)):
        tag.extract()

    # REGEX function HERE to sanitize url
    # removes any fragments
    #strCompleteURL = tutils.removeFragment(url)
    #strCompleteURL = tutils.removeFragment(strCompleteURL)url[0]
    #check if url is valid before storing

    #else:
        #r.sadd(blackList, url)
        #return
        #DataStore.urlSeenBefore.add(strCompleteURL)
    #if not r.sismember(urlSet,strCompleteURL):

        #DataStore.uniqueUrlCount += 1

    # increment counter for Domain based on subdomain
    tutils.incrementSubDomain(url)

    # add all tokens found from html response with tags removed
    varTemp = soup.get_text()
    tutils.tokenize(url, varTemp)

    for link in soup.find_all('a'):
        # get absolute urls here before adding to listLInks()
        childURL = link.get('href')

        # REGEX function HERE to sanitize url and/or urljoin path to hostname
        if(childURL != None):
            url = tutils.returnFullURL(url, childURL)

        if not tutils.isValid(url): #skip invalid urls
            continue

        if(len(url) > 0):
            listLinks.append(url)

    return listLinks    #returns the urls to the Frontier object

