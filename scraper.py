import re
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser as RobotFileParser
from bs4 import BeautifulSoup

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]   #automatically adds to frontier

def extract_next_links(url, resp):
    parsed_uri = urlparse('http://stackoverflow.com/questions/1234567/blah-blah-blah-blah')
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

    robot = RobotFileParser(result + "robots.txt")
    robot.read()
    boolCanFetch = robot.can_fetch("*", robot.url)

    listLinks = list()

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    print("complete")

    for link in soup.find_all('a'):
        listLinks.append(link.get('href'))

    if len(listLinks) > 0:
        print(listLinks)

    listLinks.append("https://www.ics.uci.edu/about/visit/index.php")

    return listLinks

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
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