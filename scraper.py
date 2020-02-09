import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup , Comment
#import crawler.datastore as data
from crawler.datastore import DataStore
import utils.team_utils as tutils
from urllib.robotparser import RobotFileParser
import redis
import Levenshtein
import requests
r = redis.Redis(host="localhost",port=6379,db=0)
# Not sure if we should have this. From a yt vid I watched
# https://www.youtube.com/watch?v=dlI-xpQxcuE

#r.set('language', 'Python', px = 10000)


visitedURL="urls"
uniqueUrl = "unique"
blackList = "blackListed"
robotsCheck ="robotsDict"
storeSeeds = 0;
repeatedUrl = ['url',0]#If we visit the same url 3 times in a row, add it to blacklist and skip.

def scraper(url, resp):
    global storeSeeds
    if storeSeeds == 0:#Store seed robot.txts only once.
        tutils.robotsTxtParseSeeds()
        storeSeeds += 1
    links = extract_next_links(url, resp)
    if(links != None):
        validLinks = []
        for link in links:
            if is_valid(link):
                #DataStore.urlSeenBefore.add(link)# ADDED AS OF 2/9 2AM
                r.sadd(visitedURL,link)
                str=tutils.removeFragment(link)
                r.sadd(uniqueUrl,str)
                validLinks.append(link)
                tutils.robotsTxtParse(url)
            else:
                r.sadd(blackList, url)
        return validLinks#[link for link in links if is_valid(link)]   #automatically adds to frontier
    else:
        return list()

def extract_next_links(url, resp):
    listLinks = list()

    if Levenshtein.distance(url, tutils.four0four) <= 10:
        return
    if (resp.status > 599): # in case we got out of seed domains
        #r.sadd(blackList,url)
        return  #maybe add to blacklist instead of returning

    if (resp.status > 400 and resp.status < 500): # should we avoid 400 statuses?
        tutils.four0four=url
        r.sadd(blackList,url)
        return  #maybe add to blacklist instead of returning

    #if(resp.status == 200):
        #Invul said he will look at this later.
        #https://stackoverflow.com/questions/37314246/how-to-get-size-of-a-file-from-webpage-in-beautifulsoup
        #res = requests.head(url)
        #if 'content-length' in res.headers and int(res.headers['content-length']) < 500 and int(res.headers['content-length']) > 6000000:
            #print("NOT ENOUGH CONTENT")
            #return
    if is_valid(url):
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

        if(len(url) > 0):
            listLinks.append(url)

    return listLinks    #returns the urls to the Frontier object

def is_valid(url):
    try:
        parsed = urlparse(url)
        subdomain = tutils.getSubDomain(url)#key = '://'.join([tutils.getSubDomain(url), parsed.scheme])

        if parsed.scheme not in set(["http", "https"]):
            return False
        if not tutils.isValid(url):
            return False
        #if url in DataStore.blackList:
        #if r.sismember(visitedURL,url):
            #return False
        if subdomain in DataStore.robotsCheck.keys():
        #if r.hexists(robotsCheck,subdomain):
            #robot = r.hget(robotsCheck,subdomain).decode('utf-8')
            robot =  DataStore.robotsCheck[subdomain]
            return robot.can_fetch("*", url)
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise