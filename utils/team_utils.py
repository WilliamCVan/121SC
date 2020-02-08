import crawler.datastore as data
from crawler.datastore import DataStore
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import re
from urllib.parse import urljoin
from utils import normalize, get_urlhash

import tldextract

def robotsTxtParse(url):
    # Finds the robot.txt of a domain and subdomain(if one exists) and
    # Stores it in DataStore.RobotChecks
    # QUESTION: Should we have the check for robotsCheck before inside function or before calling it?

    domain = getDomain(url)
    robot = RobotFileParser()
    robot.set_url(domain)
    robot.read()

    if domain != '' and domain not in DataStore.robotsCheck:
        DataStore.robotsCheck[domain] = robot

    subdomain = getSubDomain(url)
    if subdomain != '' and subdomain not in DataStore.robotsCheck:
        robot = RobotFileParser()
        robot.set_url(subdomain)
        robot.read()

        DataStore.robotsCheck[subdomain] = robot

def robotsTxtParseSeeds():
    # Stores the robot.txt of the seed urls in DataStore.RobotChecks
    seedUrls = ['https://www.ics.uci.edu',
    'https://www.cs.uci.edu',
    'https://www.informatics.uci.edu',
    'https://www.stat.uci.edu',
    'https://today.uci.edu/department/information_computer_sciences/']
    for seedUrl in seedUrls:
        domain = getSubDomain(seedUrl)
        robot = RobotFileParser()
        robot.set_url(domain)
        robot.read()
        DataStore.robotsCheck[domain] = robot

def getDomain(url):
    # Gets the domain or subdomain of a url and returns it.

    ext = tldextract.extract(url)
    domainUrl = ext.domain
    domainUrl = '.'.join(domainUrl, ext.suffix)

    return domainUrl

def getSubDomain(url):
    ext = tldextract.extract(url)
    domainUrl = ''
    if ext.subdomain == '':  # Returns url with subdomain attached.
        return domainUrl
    domainUrl = '.'.join(ext[:2])
    domainUrl = '.'.join(domainUrl, ext.suffix)

    return domainUrl

def returnFullURL(parent_url, strInput):
    parsed_uri = urlparse(parent_url)
    result = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)   #remove slash

    if (strInput.strip() == "/"):
        return ""
    if (strInput.strip() == "#"):
        return ""
    if ("#" in strInput.strip() and findUrl(strInput) == ""):
        return ""
    else:
        return urljoin(result, strInput)



def incrementSubDomain(strDomain):
    parsed_uri = urlparse(strDomain)
    # MAYBE remove the uri.scheme, since it doesn't matter the protocol #
    result = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)   #remove slash at end

    DataStore.subDomainCount[result] = DataStore.subDomainCount.get(result, 0) + 1

    if "ics.uci.edu" in result:
        if strDomain not in DataStore.urlSeenBefore:
            DataStore.icsSubDomains[result] += 1
        elif strDomain not in DataStore.icsSubDomains.keys():
            DataStore.icsSubDomains[result]

def printIcsSubDomains():
    #Prints out the subdomains in alphabetical order, along with the amount of unique pages
    sortedDomains = [(subDomain, pageCount) for subDomain, pageCount in DataStore.icsSubDomains]
    sortedDomains.sort(key = lambda x: x[0])
    for subDomain, pageCount in sortedDomains:
        print(f"{subDomain} -> {pageCount}")


def tokenize(url, rawText):
    listTemp = re.split(r'[^a-z0-9]+', rawText.lower())

    if(DataStore.mostTokensUrl[1] < len(listTemp)):
        DataStore.mostTokensUrl[0] = url
        DataStore.mostTokensUrl[1] = len(listTemp)

    for word in listTemp:
        if (len(word) > 0):
            DataStore.tokensCount[word] = DataStore.tokensCount.get(word, 0) + 1

    if (len(listTemp) == 0):
        DataStore.blackList.add(url)


#if url has been blacklisted before
def isBlackListed(str):
    if str in DataStore.blackList:
        return True
    return False

#extract url
def findUrl(str):
    try:
        url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str)
        if ',' in url[0]:
            url= url[0].split(',')
        return url
    except:
        return ""


def removeQuery(str):
    str = str.split('?')[0]
    return str


# def hashUrl(url)->None:
#     # 2/6/2020 Function takes in a url and finds the hash for it. Adds the hash and url into a dic
#     normalizedUrl = normalize(url)
#     DataStore.hashTable[get_urlhash(normalizedUrl)] = url

#does the url contain duplicate paths
def multipleDir(str):
    dict={}
    url = str.split('/')
    for i in url:
        if i in dict:
            dict[i] +=1
            DataStore.blackList.add(str)
            return True
        else:
            dict[i] = 1
    return False

def ifConsideredSpam(str):
    try:
        str = str.split('?')[1]
        str = str.split('=')[0]
        if "replytocom" in str:
            return True
    except:
        return False
    return False

def ifInUCIDomain(str):
    try:
        str = str.split('?')[0]
        if 'uci.edu'in str:
            return True
        return False
    except:
        return False

#is url valid
def isValid(str):
    url = findUrl(str)

    if isBlackListed(str):
        return False
    if str in DataStore.urlSeenBefore:
        return False
    if multipleDir(str):
        return False
    if ifConsideredSpam(str):
        return False
    if ifInUCIDomain(str) == False:
        return False
    return True