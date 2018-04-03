import bisect
from bs4 import BeautifulSoup
from random import randint
import re
import requests
from time import sleep

from utils.sort import index


# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
def is_downloadable(url, mimes, session=None, timeout_min=5, timeout_max=10):
    """
        Return True if the URL Content-Type entity header contains a MIME type
            that suggest a downloadable URL
        :param mimes: values that suggest a downloadable URL
        :param (optional) session: http://docs.python-requests.org/en/master/user/advanced/#session-objects
        :param (optional) timeout: timeout in seconds between each HEAD request
    """
    sleep(randint(timeout_min, timeout_max))
    try:
        if session:
            r = session.head(url)
        else:
            r = requests.head(url)
    except requests.exceptions.RequestException as e:
        # The best approach would be to log this failed HEAD request
        #   attempt
        print(f'HEAD request on {url} raised {e}')
        return False 
    content_type = r.headers.get('content-type')
    if content_type: 
        # This could be optimized (although set lookups are very fast). See
        # https://stackoverflow.com/questions/7380629/perform-a-binary-search-for-a-string-prefix-in-python
        for m in mimes:
            if re.findall(m, content_type):
               return True 
    return False
def downloadable_urls(urls, session, domains, mimes, visited=[], timeout_min=5,
        timeout_max=10):
    while urls:
        url = urls.pop()
        if is_downloadable(url, mimes, session, timeout_min, timeout_max):
            yield url
        else:
            # Save bandwidth (and time) by performing a GET on
            #   non-downloadable URLs
            sleep(randint(timeout_min, timeout_max))
            try:
                r = session.get(url)
            except requests.exceptions.RequestException as e:
                print(f'HEAD request on {url} raised {e}')
                # Could also log the exception for future inspection
                continue
            else:
                soup = BeautifulSoup(r.text, 'lxml')
                for link in soup.find_all('a'):
                    href = link.get('href')
                    # Another optimization: only add hrefs within the
                    #   domains 
                    if href:
                        try:
                            _ = index(visited, href)
                        except ValueError:  # href not in visited
                            bisect.insort(visited, href)
                            for domain in domains:
                                if re.findall(domain, href):
                                    urls.add(href)
                yield from downloadable_urls(urls, session, domains,
                            mimes, visited, timeout_min, timeout_max)
def download(url, saveas, stream=False, chunk_size=None):
    r = requests.get(url, stream=stream)
    with open(saveas, 'wb') as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            f.write(chunk)
