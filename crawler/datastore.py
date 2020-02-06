import utils.team_utils as tutils

class DataStore:
    robotsCheck = dict()
    subDomainCount = dict()
    tokensCount = dict()
    urlSeenBefore = set()
    blackList = set()

    def __init__(self, corpus, frontier):
        #tutils.robotsTxtParse()
        print()