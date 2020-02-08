import crawler.datastore as data
from crawler.datastore import DataStore
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser as RobotFileParser
import re
from urllib.parse import urljoin

def robotsTxtParse():
    parsed_uri = urlparse('https://www.ics.uci.edu')
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

    robot = RobotFileParser(result + "robots.txt")
    robot.read()
    boolCanFetch = robot.can_fetch("*", robot.url)
    DataStore.robotsCheck[result] = robot


def returnFullURL(parent_url, strInput):
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parent_url)
    if (strInput.strip() == "/"):
        return ""
    if (strInput.strip() == "#"):
        return ""
    if ("#" in strInput.strip() and findUrl(strInput) == False):
        return ""
    else:
        return urljoin(parent_url, strInput)



def incrementSubDomain(strDomain):
    parsed_uri = urlparse(strDomain)
    # MAYBE remove the uri.scheme, since it doesn't matter the protocol #
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

    DataStore.subDomainCount[result] = DataStore.subDomainCount.get(result, 0) + 1

def tokenize(url, rawText):
    listTemp = re.split(r'[^a-z0-9]+', rawText.lower())

    for word in listTemp:
        if (len(word) > 0):
            DataStore.tokensCount[word] = DataStore.tokensCount.get(word, 0) + 1

    if (len(listTemp) == 0):
        DataStore.blackList.add(url)

#if the url has been seen before or is in the frontier now
def isDuplicateUrl(str):
    if str in DataStore.frontier:
        return True
    if str in DataStore.urlSeenBefore:
        return True
    return False

#if url has been blacklisted before
def isBlackListed(str):
    if str in DataStore.blackList:
        return True
    return False

#extract url
def findUrl(str):
    # removes all the fragments from url and return url string
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str)
    if ',' in url[0]:
        url= url[0].split(',')
    return url

#is url valid
def isValid(str):
    url = findUrl(str)
    if isBlackListed(str):
        return False
    if isDuplicateUrl(str):
        return False
    return True

def removeQueue(str):
    str = str.split('?')[0]
    return str
