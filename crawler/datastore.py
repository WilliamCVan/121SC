
class DataStore:
    #team_utils could not pickup self.robotsCheck property without below declaration
    robotsCheck = dict()
    subDomainCount = dict()
    tokensCount = dict()
    urlSeenBefore = set()
    frontier = set()
    blackList = set()

    uniqueUrlCount = 0
    mostTokensUrl = ("", 0) #[url, count]

    def __init__(self):
        self.robotsCheck = dict()
        self.subDomainCount = dict()
        self.tokensCount = dict()
        self.urlSeenBefore = set()
        self.blackList = set()
        self.frontier = set()
        # Read robots.txt for all domains and store in dict
        #tutils.robotsTxtParse()

        print()