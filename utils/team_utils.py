from crawler.datastore import DataStore
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import re
from urllib.parse import urljoin
from utils import normalize, get_urlhash
import redis
import tldextract

r = redis.Redis(host="localhost",port=6379,db=0)

# Not sure if we should have this. From a yt vid I watched
# https://www.youtube.com/watch?v=dlI-xpQxcuE

#r.set('language', 'Python', px = 10000)


robotsCheck ="robotsDict"
mostTokensUrl="mostTokens"
setDomainCount = "setDomainCount"
tokenCount = "tokenCount"
blackList = "blackListed"
visitedURL = "urls"
#ask artur for explination these are actually pretty useful
four0four = ""


icsDomains = {}#Added to keep track of specifically ics Domains

'''
Finds the domain/subdomain of url gets robots.txt
Stores the domain/subdomain as a key in robotsCheck
I think we just need to call subdomain(url) to get a key, because all urls should have the 5 seeds as their domain.
May remove adding domain to robotchecks part.

Thought process: robots.txt is found in the root page which is usually a domain or subdomain. In order to check if a url is allowed or not, 
just find its domain/subdomain and look at the disallowed section.
'''
def robotsTxtParse(url):
    # Finds the robot.txt of a domain and subdomain(if one exists) and
    # Stores it in DataStore.RobotChecks
    scheme = urlparse(url).scheme #scheme needed to read robots.txt

    domain = getDomain(url)
    #val=r.hget(robotsCheck,"bhh").decode('utf-8')
    if domain != '' and domain not in DataStore.robotsCheck:
    #if domain != '' and not r.hexists(robotsCheck, domain):
        robotTxtUrl = f"{scheme}://{domain}/robots.txt"  # '://'.join([scheme, subdomain])#add scheme to subdomain
        robot = RobotFileParser()
        robot.set_url(robotTxtUrl)
        robot.read()
        #r.hset(robotsCheck, domain, robot)
        DataStore.robotsCheck[domain] = robot

    #if domain != '' and not r.hexists(robotsCheck,domain):
        #r.hset(robotsCheck,domain,robot)

    subdomain = getSubDomain(url)
    #if subdomain != '' and subdomain not in DataStore.robotsCheck:
    if subdomain != '' and not r.hexists(robotsCheck,subdomain):
        robotTxtUrl = f"{scheme}://{subdomain}/robots.txt" #'://'.join([scheme, subdomain])#add scheme to subdomain
        robot = RobotFileParser()
        robot.set_url(robotTxtUrl)
        robot.read()
        #r.hset(robotsCheck, subdomain, robot)
        DataStore.robotsCheck[subdomain] = robot


def robotsTxtParseSeeds():
    # Stores the robot.txt of the seed urls in DataStore.RobotChecks
    seedUrls = ['https://today.uci.edu/department/information_computer_sciences/',
    'https://www.ics.uci.edu',
    'https://www.cs.uci.edu',
    'https://www.informatics.uci.edu',
    'https://www.stat.uci.edu']
    for seedUrl in seedUrls:
        scheme = urlparse(seedUrl).scheme
        domain = getSubDomain(seedUrl)
        robotTxtUrl = f"{scheme}://{domain}/robots.txt"  # '://'.join([scheme, subdomain])#add scheme to subdomain
        robot = RobotFileParser()
        robot.set_url(robotTxtUrl)
        robot.read()
        DataStore.robotsCheck[domain] = robot

### CHANGED TO ADD SUFFIX TO DOMAIN
def getDomain(url):
    # Gets the domain or subdomain of a url and returns it.
    ext = tldextract.extract(url)
    domainUrl = ext.domain
    domainUrl = '.'.join([domainUrl, ext.suffix])

    return domainUrl

### CHANGED TO ADD SUFFIX TO DOMAIN
def getSubDomain(url):
    ext = tldextract.extract(str(url))
    domainUrl = ''
    if ext.subdomain == '':  # Returns url with subdomain attached.
        return '.'.join([ext.domain, ext.suffix])
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

    if r.hexists(setDomainCount,result):
        val = r.hget(setDomainCount,result).decode('utf-8')
        val = int(val)
        val += 1
        r.hset(setDomainCount,result,val)
    else:
        r.hset(setDomainCount,result,1)

    #r.hset(setDomainCount)
    #DataStore.subDomainCount[result] = DataStore.subDomainCount.get(result, 0) + 1


def tokenize(url, rawText):

    listTemp = re.split(r'[^a-z0-9]+', rawText.lower())


    #if r.hget(mostTokensUrl, ):
    if (DataStore.mostTokensUrl[1] < len(listTemp)):
        DataStore.mostTokensUrl[0] = url
        DataStore.mostTokensUrl[1] = len(listTemp)
        # cant find a workaround so im just storing it locally and in the database
        r.delete(mostTokensUrl)
        r.hset(mostTokensUrl,url,len(listTemp))


    for word in listTemp:
        tokens = 0
        if (len(word) > 0):
            tokens+=1
        if r.hexists(tokenCount,word):
            r.hset(tokenCount,word,tokens)
            #DataStore.tokensCount[word] = DataStore.tokensCount.get(word, 0) + 1

    if (len(listTemp) == 0):
        r.sadd(blackList,url)
        #DataStore.blackList.add(url)


#### ADDED IF STATEMENTS TO CHECK FOR CALENDAR
#if url has been blacklisted before
def isBlackListed(str):
    # if r.sismember(blackList,str):
    # #if str in DataStore.blackList:
    #     return True
    if 'https://today.uci.edu/department/information_computer_sciences/calendar' in str:
        return True
    elif 'https://today.uci.edu/calendar' in str:
        return True

    return False

#supposed to split if two urls combined
# https://canvas.eee.uci.edu/courses/23516/files/folder/lectures?preview-8330088 returns empty when run on
def extractURL(str):
    try:
        url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str)
        if ',' in url[0]:
            url= url[0].split(',')
        return url
    except:
        return ""

def removeFragment(str):
    str = str.split('#')[0]
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
            r.sadd(blackList,str)
            #DataStore.blackList.add(str)
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
    str = removeFragment(str)

    if isBlackListed(str):
        return False
    #if  r.sismember(blackList, str):
    #if str in DataStore.blackList:#r.sismember(urlSet,str):
        #return False

    # if r.sismember(visitedURL, str):
    # #if str in DataStore.urlSeenBefore:# ADDED CHECK AS OF 2/9 2AM
    #     return False
    if not is_validDEFAULT(str):
        return False
    if multipleDir(str):
        return False
    if ifConsideredSpam(str):
        return False
    if not ifInUCIDomain(str):
        return False
    if badUrl(str):
        return False
    return True

def badUrl(str):
    if "search" in str:
        return True
    if "sid" in str:
        return True
    #if "&" in str:
     #   return True
    if "calendar" in str:
        return True
    if "graphics" in str:
        return True
    if "color" in str:
        return True
    if "ppt" in str:
        return True
    if "pdf" in str:
        return True
    if "year" in str:
        return True
    if len(str)>150:
        return True
    if "login" in str:
        return True
    if "://cbcl" in str:
        return False
    if "www.amazon.com" in str:
        return False
    if "difftype=sidebyside" in str:
        return False
    # Comment out 2/9/2020 at 3:26PM
    # Try re-running crawler with updated rules
    # if "http://cellfate.uci.edu" in str:
    #     return False
    # if "https://ugradforms.ics.uci.edu" in str:
    #     return False
    # if "http://catalogue.uci.edu" in str:
    #     return False
    # if "http://www.studyabroad.uci.edu" in str:
    #     return False
    return False

def robotsAllowsSite(subdomain, url):
    if subdomain in DataStore.robotsCheck.keys():
        # if r.hexists(robotsCheck,subdomain):
        # robot = r.hget(robotsCheck,subdomain).decode('utf-8')
        robot = DataStore.robotsCheck[subdomain]
        return robot.can_fetch("*", url)

def is_validDEFAULT(url):
    try:
        parsed = urlparse(url)
        subdomain = getSubDomain(url)#key = '://'.join([tutils.getSubDomain(url), parsed.scheme])

        if parsed.scheme not in set(["http", "https"]):
            return False

        if not robotsAllowsSite(subdomain, url):
            return False
        #if url in DataStore.blackList:
        #if r.sismember(visitedURL,url):
            #return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|jpg|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4|rvi"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
    except TypeError:
        print ("TypeError for ", parsed)
        return False

        # if subdomain in DataStore.robotsCheck.keys():
        # #if r.hexists(robotsCheck,subdomain):
        #     #robot = r.hget(robotsCheck,subdomain).decode('utf-8')
        #     robot =  DataStore.robotsCheck[subdomain]
        #     return robot.can_fetch("*", url)


'''
Problem 3

What are the 50 most common words in the entire set of pages? 
(Ignore English stop words, which can be found, for example, here (Links to an external site.))
 Submit the list of common words ordered by frequency.
 
 STILL NEEDS TO ACCOUNT FOR STOP WORDS
 
 Thought Process: If I am understandign tokenization correctly, all words and their weights are stored in tokensCount.
 So in order to find the 50 most used words I just need to sort the key: vals of the dict into a list by decreasing
 weight value.
 
 After I have printed 50 entries, exit the method.
'''
def reportQuestion3():
    count = 0
    for word, weight in sorted([(k, v) for k, v in DataStore.tokensCount.items()], key=lambda x: -x[1]):
        print(f"{word}->{weight}")
        count+= 1
        if count >= 50:
            return

'''
Problem 4

How many subdomains did you find in in the ics.uci.edu domain? 
Submit the list of subdomains ordered alphabetically and the number 
of unique pages detected in each subdomain. The content of this list should 
be lines containing URL, number, for example:

Thought Process: Since we have a set of all the urls we have crawled, I need to filter through them to find sites
that are subdomains of ics.uci.edu. 

I iterate through the urls, checking if they have ics.uci.edu in the subdomain.
If they have it, store the url because it is part of ics.uci.edu subdomains.
Store the subdomain itself in a dict to reference later for unique page counts.

Iterate through the filtered pages, and lookup the subdomain they of ics.uci.edu they belong to.
Increment count by 1.
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


# def ifrepeats():
#     str = "/grad/student-profiles/grad/graduate-student-profile-christina-rall/"
#     arrsplit = str.split("/");
#     iCount = 0
#     strcurrent = ""
#     loopiter = 0
#
#     for itoken in arrsplit:
#         if loopiter == 0:
#             strcurrent = arrsplit[0]
#             continue
#
#         while len(arrsplit) > 0:
#             if len(itoken.strip()) == 0:
#                 continue
#
#             if (strcurrent == itoken):
#                 return True
#
#         if len(arrsplit) > 0:
#             arrsplit = arrsplit[1:]
#         loopiter = loopiter + 1
#
# abc = ifrepeats()
# print(abc)


