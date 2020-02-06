import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import crawler.datastore as data
import utils.team_utils as tutils

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]   #automatically adds to frontier

def extract_next_links(url, resp):
    listLinks = list()
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

    strCompleteURL = url  # REGEX function HERE to sanitize url

    # increment counter for Domain based on subdomain
    tutils.incrementSubDomain(url)

    # add all tokens found from html response with tags removed
    tutils.tokenize(soup.get_text())


    for link in soup.find_all('a'):
        strCompleteURL = link.get('href') #REGEX function HERE to sanitize url and/or urljoin path to hostname

        listLinks.append(strCompleteURL)

    return listLinks    #returns the urls to the Frontier object

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if url in data.DataStore.blackList:
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