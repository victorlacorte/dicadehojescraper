import bisect
from bs4 import BeautifulSoup
import re
import requests

from utils.sort import index


# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
def is_downloadable(url, mimes, session=None):
    """
        Return True if the URL Content-Type entity header contains a MIME type
            that suggest a downloadable URL
        :param url: URL to analyze
        :param mimes: values that suggest a downloadable URL
        :param (optional) session: http://docs.python-requests.org/en/master/user/advanced/#session-objects
    """
    try:
        if session:
            r = session.head(url)
        else:
            r = requests.head(url)
    except requests.exceptions.RequestException:
        # The best approach would be to log this failed HEAD request attempt
        return False
    content_type = r.headers.get('content-type')
    if content_type: 
        for m in mimes:
            if re.findall(m, content_type):
                return True
    return False
def downloadable_urls(urls, session, domains, mimes, visited=[]):
    while urls:
        url = urls.pop()
        if is_downloadable(url, mimes, session):
            yield url
        else:
            # Save bandwidth (and time) by performing a GET on
            #   non-downloadable URLs
            try:
                r = session.get(url)
            except requests.exceptions.RequestException:
                # Could also log the exception for future inspection
                pass
            else:
                soup = BeautifulSoup(r.text, 'lxml')
                for link in soup.find_all('a'):
                    href = link.get('href')
                    # Another optimization: only add hrefs within the
                    #   domains 
                    if href:
                        try:
                            _ = index(visited, href)
                        except ValueError:
                            bisect.insort(visited, href)
                            for domain in domains:
                                if re.findall(domain, href):
                                    print(href)
                                    urls.add(href)
                yield from downloadable_urls(urls, session, domains,
                            mimes, visited)
def download(url, saveas, stream=False, chunk_size=None):
    r = requests.get(url, stream=stream)
    with open(saveas, 'wb') as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            f.write(chunk)
