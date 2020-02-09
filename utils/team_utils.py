from crawler.datastore import DataStore
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import re
from urllib.parse import urljoin
from utils import normalize, get_urlhash
import redis
import tldextract

#r = redis.Redis(host="localhost",port=6379,db=0)

# Not sure if we should have this. From a yt vid I watched
# https://www.youtube.com/watch?v=dlI-xpQxcuE

#r.set('language', 'Python', px = 10000)


#robotsCheck ="robotsDict"
#mostTokensUrl="mostTokens"
#setDomainCount = "setDomainCount"
#tokenCount = "tokenCount"
#blackList = "blackListed"
#urlSet = "urls"

icsDomains = {}#Added to keep track of specifically ics Domains

'''
Finds the domain/subdomain of url gets robots.txt
Stores the {scheme}://{domain/subdomain} as a key in robotsCheck
In order to check if url is in the robots.txt of a file, either iterate through robotsCheck
or call getSubDomain(url) and urlparse(url).scheme to combine them to form the key. Ex in scraper.py is_valid
'''
def robotsTxtParse(url):
    # Finds the robot.txt of a domain and subdomain(if one exists) and
    # Stores it in DataStore.RobotChecks
    scheme = urlparse(url).scheme #scheme needed to read robots.txt

    domain = getDomain(url)
    #val=r.hget(robotsCheck,"bhh").decode('utf-8')
    if domain != '' and domain not in DataStore.robotsCheck:
        domain = '://'.join([scheme, domain])#add scheme to domain
        robot = RobotFileParser()
        robot.set_url('://'.join([domain, 'robots.txt']))
        robot.read()
        DataStore.robotsCheck[domain] = robot

    #if domain != '' and not r.hexists(robotsCheck,domain):
        #r.hset(robotsCheck,domain,robot)

    subdomain = getSubDomain(url)
    if subdomain != '' and subdomain not in DataStore.robotsCheck:
    #if subdomain != '' and not r.hexists(robotsCheck,subdomain):
        subdomain = '://'.join([scheme, subdomain])#add scheme to subdomain
        robot = RobotFileParser()
        robot.set_url('/'.join([subdomain,'robots.txt']))
        robot.read()

        DataStore.robotsCheck[subdomain] = robot
        #r.hmset(robotsCheck,subdomain,robot)

def robotsTxtParseSeeds():
    # Stores the robot.txt of the seed urls in DataStore.RobotChecks
    seedUrls = ['https://today.uci.edu/department/information_computer_sciences/',
    'https://www.ics.uci.edu',
    'https://www.cs.uci.edu',
    'https://www.informatics.uci.edu',
    'https://www.stat.uci.edu']
    for seedUrl in seedUrls:
        scheme = urlparse(seedUrl).scheme
        domain = '://'.join([scheme, getSubDomain(seedUrl)])
        robot = RobotFileParser()
        robot.set_url('/'.join([domain,'robots.txt']))
        robot.read()
        #r.hmset(robotsCheck, domain, robot)
        DataStore.robotsCheck[domain] = robot

### CHANGED TO ADD SCHEME AND SUFFIX TO DOMAIN
def getDomain(url):
    # Gets the domain or subdomain of a url and returns it.
    ext = tldextract.extract(url)
    domainUrl = ext.domain
    domainUrl = '.'.join([domainUrl, ext.suffix])

    return domainUrl

### CHANGED TO ADD SCHEME AND SUFFIX TO DOMAIN
def getSubDomain(url):
    ext = tldextract.extract(url)
    domainUrl = ''
    if ext.subdomain == '':  # Returns url with subdomain attached.
        return '.'.join([domainUrl, ext.suffix])
    domainUrl = '.'.join(ext[:2])
    domainUrl = '.'.join([domainUrl, ext.suffix])

    return domainUrl


def returnFullURL(parent_url, strInput):
    parsed_uri = urlparse(parent_url)
    result = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)   #remove slash

    if (strInput.strip() == "/"):
        return ""
    if (strInput.strip() == "#"):
        return ""
    if ("#" in strInput.strip() and removeFragment(strInput) == ""):
        return ""
    else:
        return urljoin(result, strInput)


def incrementSubDomain(strDomain):
    parsed_uri = urlparse(strDomain)
    # MAYBE remove the uri.scheme, since it doesn't matter the protocol #
    result = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)   #remove slash at end

    #r.hset(setDomainCount)
    DataStore.subDomainCount[result] = DataStore.subDomainCount.get(result, 0) + 1


def tokenize(url, rawText):

    listTemp = re.split(r'[^a-z0-9]+', rawText.lower())

    #if r.hget(mostTokensUrl,)

    if(DataStore.mostTokensUrl[1] < len(listTemp)):
        DataStore.mostTokensUrl[0] = url
        DataStore.mostTokensUrl[1] = len(listTemp)
        # cant find a workaround so im just storing it locally and in the database
        #r.delete(mostTokensUrl)
        #r.hset(mostTokensUrl,url,len(listTemp))

    for word in listTemp:
        tokens = 0
        if (len(word) > 0):
            tokens+=1
            #r.hset(tokenCount,word,tokens)
            DataStore.tokensCount[word] = DataStore.tokensCount.get(word, 0) + 1

    if (len(listTemp) == 0):
        #r.sadd(blackList,url)
        DataStore.blackList.add(url)


#### ADDED IF STATEMENTS TO CHECK FOR CALENDAR
#if url has been blacklisted before
def isBlackListed(str):
    #if r.sismember(blackList,str):
    if str in DataStore.blackList:
        return True
    elif 'https://today.uci.edu/department/information_computer_sciences/calendar/' in str:
        return True
    elif 'https://today.uci.edu/calendar' in str:
        return True

    return False

#extract url
def removeFragment(str):
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
            #r.sadd(blackList,str)
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
    url = removeFragment(str)

    if isBlackListed(str):
        return False
    if str in DataStore.blackList:#r.sismember(urlSet,str):
        return False
    if multipleDir(str):
        return False
    if ifConsideredSpam(str):
        return False
    if ifInUCIDomain(str) == False:
        return False
    return True


'''
What are the 50 most common words in the entire set of pages? 
(Ignore English stop words, which can be found, for example, here (Links to an external site.))
 Submit the list of common words ordered by frequency.
'''
def reportQuestion3():
    count = 0
    for word, weight in sorted([(k, v) for k, v in DataStore.tokensCount.items()], key=lambda x: -x[1]):
        print(f"{word}->{weight}")
        count+= 1
        if count >= 50:
            return

'''
Retrieves all the data needed to answer question 4.
NOT DONE YET. Still need to figure out redis. Kinda like pseudo code.


How many subdomains did you find in in the ics.uci.edu domain? 
Submit the list of subdomains ordered alphabetically and the number 
of unique pages detected in each subdomain. The content of this list should 
be lines containing URL, number, for example:
'''
def reportQuestion4():
    subdomainCount = 0

    subdomainDict = dict()
    subdomainPageSet = set()
    uniquePages = 0

    # Find all the subdomains under ics.uci.edu
    for url in DataStore.urlSeenBefore:
        subdomain = getSubDomain(url)
        if 'ics.uci.edu' in subdomain:# Find subdomain of ics.uci.edu
            if subdomain not in subdomainDict.keys():# Making sure url was not a dif page of a seen subdomain
                subdomainCount += 1
                subdomainDict[subdomain] = 0
            parsedUrl = removeFragment(url)
            subdomainPageSet.add(parsedUrl)

    # Iterates through filtered pages. Find the subdomain each page belongs to and increment the unique page count for it.
    for url in  subdomainPageSet:
        subdomain = getSubDomain(url)
        subdomainDict[subdomain] += 1

