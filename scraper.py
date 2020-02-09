import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup , Comment
#import crawler.datastore as data
from crawler.datastore import DataStore
import utils.team_utils as tutils
from urllib.robotparser import RobotFileParser
import redis

r = redis.Redis(host="localhost",port=6379,db=0)
urlSet="urls"
startUp = 0#var so robotsTxtParseSeeds only runs once

def scraper(url, resp):
    links = extract_next_links(url, resp)
    if(links != None):
        return [link for link in links if is_valid(link)]   #automatically adds to frontier
    else:
        return list()

def extract_next_links(url, resp):
    global startUp

    listLinks = list()
    if (resp.status > 599): # in case we got out of seed domains
        return  #maybe add to blacklist instead of returning

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

    tutils.robotsTxtParse(url)
    if startUp == 0:
        tutils.robotsTxtParseSeeds()
        startUp += 1

    for tag in soup(text=lambda text: isinstance(text,Comment)):
        tag.extract()

    # REGEX function HERE to sanitize url
    # removes any fragments
    strCompleteURL = tutils.findUrl(url)[0]
    #check if url is valid before storing
    if tutils.isValid(strCompleteURL):
        r.sadd(urlSet,strCompleteURL)
    #DataStore.urlSeenBefore.add(strCompleteURL)
    #if not r.sismember(urlSet,strCompleteURL):

        #DataStore.uniqueUrlCount += 1

    # increment counter for Domain based on subdomain
    tutils.incrementSubDomain(strCompleteURL)

    # add all tokens found from html response with tags removed
    varTemp = soup.get_text()
    tutils.tokenize(strCompleteURL, varTemp)

    for link in soup.find_all('a'):
        # get absolute urls here before adding to listLInks()
        childURL = link.get('href')

        # REGEX function HERE to sanitize url and/or urljoin path to hostname
        if(childURL != None):
            strCompleteURL = tutils.returnFullURL(strCompleteURL, childURL)

        if(len(strCompleteURL) > 0):
            listLinks.append(strCompleteURL)

    return listLinks    #returns the urls to the Frontier object

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if not tutils.isValid(url):
            return False
        if url in DataStore.blackList:
            return False
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