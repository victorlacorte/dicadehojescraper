from bs4 import BeautifulSoup
import os
import requests


# def file_like(url):
#     _, ext = os.path.splitext(url)
#     if ext:
#         return True
#     return False
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
def is_downloadable(url, session=None, mimes=['text/html']):
    """
        Return True if the URL Content-Type entity header contains a MIME type
            that suggest a downloadable URL
        :param url: URL to analyze
        :param session: http://docs.python-requests.org/en/master/user/advanced/#session-objects
        :param mimes: values that suggest a _non_ downloadable URL
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
        # If we find any match on the MIMEs list the URL is _not_ downloadable,
        # so we negate the result to obtain the desired return value
        return not any(_ in content_type.lower() for _ in mimes)
    return False
# TODO this algorithm is flawed by design: we need to expand URLs and consume
#   them all to avoid repetition (
# def url_expander(url, session, base_url=base_url, visited=[]):
#     """
#         :param base_url: retrict search scope to a specific domain
#         :param visited: visited URLs
#     """
#     print(url)
#     if base_url in url and url not in visited:
#         visited.append(url)
#         if file_like(url):
#             yield url
#         else:
#             r = session.get(url)
#             soup = BeautifulSoup(r.text, 'lxml')
#             for link in soup.find_all('a'):
#                 href = link.get('href')
#                 if href:
#                     yield from url_expander(href, session, base_url, visited)
# def url_expander2(urls, session, base_url=base_url, visited=[]):
#     while urls:
#         url = urls.pop()
#         print(url)
#         if base_url in url and url not in visited:
#             visited.append(url)
#             # TODO improve this type of recognition
#             if file_like(url):
#                 yield url
#             else:
#                 r = session.get(url)
#                 soup = BeautifulSoup(r.text, 'lxml')
#                 for link in soup.find_all('a'):
#                     href = link.get('href')
#                     if href:
#                         urls.add(href)
#                 yield from url_expander2(urls, session, base_url, visited)
def downloadable_urls(urls, session, domains, visited=[]):
    while urls:
        url = urls.pop()
        print(url)
        # Probably don't need to verify if the URL is within the domains
        #   since we do that when adding the hrefs
        #if any(_ in url for _  in domains) and url not in visited:
        if url not in visited:
            visited.append(url)
            if is_downloadable(url, session):
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
                        if href and any(_ in href for _ in domains):
                            urls.add(href)
                    yield from downloadable_urls(urls, session, domains,
                            visited)
