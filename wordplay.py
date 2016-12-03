'''
Dowload and display stats about WXPN's A-Z songs playlist
'''

# imports
import urllib
import urlparse
import re

# function definitions
def get_songs(url='http://origin.xpn.org/static/az.php', letter='a',
                  pattern=r'<li>([^<]+) - ([^<]+)</li>'):
    '''
    Download data from the provided url, querying for all songs that start with
    the given letter and return a list of songs. Url text is parsed usign the
    regular expression pattern.
    '''

    # construct the url, adding a query for the given letter
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update({'q':letter})
    url_parts[4] = urllib.urlencode(query)
    full_url = urlparse.urlunparse(url_parts)

    # Read the url
    try:
        ufile = urllib.urlopen(full_url)  # get file-like object for url
        info = ufile.info()   # meta-info about the url content
        if info.gettype() == 'text/html':
            url_text = ufile.read()  # read all its text
    except IOError:
        url_text = ''
        print 'problem reading url:', full_url

    # Parse the url text into a list of tuples (title, artist)
    pattern = r'<li>([^<]+) - ([^<]+)</li>'
    songs = re.findall(pattern, url_text)

    return songs


