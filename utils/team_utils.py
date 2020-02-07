import crawler.datastore as data
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser as RobotFileParser
import re

def robotsTxtParse():
    parsed_uri = urlparse('https://www.ics.uci.edu')
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

    robot = RobotFileParser(result + "robots.txt")
    robot.read()
    boolCanFetch = robot.can_fetch("*", robot.url)
    data.DataStore.robotsCheck[result] = robot

def incrementSubDomain(strDomain):
    parsed_uri = urlparse(strDomain)
    # MAYBE remove the uri.scheme, since it doesn't matter the protocol #
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

    data.DataStore.subDomainCount[result] += 1

def tokenize(url, rawText):
    listTemp = re.split(r'[^a-z0-9]+', rawText.lower())

    for word in listTemp:
        if (len(word) > 0):
            data.DataStore.tokensCount[word] = data.DataStore.tokensCount.get(word, 0) + 1

    if (len(listTemp) == 0):
        data.DataStore.blackList.add(url)