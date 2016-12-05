'''
Functions to download and display stats about WXPN's A-Z songs playlist

Author: Lena Bartell, github.com/lbartell
'''

# imports
import urllib
import urlparse
import re
import string
import discogs_client
import warnings

# function definitions
def parse_url(url='http://origin.xpn.org/static/az.php', query='a',
                  pattern=r'<li>([^<]+) - ([^<]+)</li>', remove_duplicates=True):
    '''
    Download data from the provided url, adding the given query and return a
    list of the results matching the regular expression given in pattern.
    '''

    # construct the url, adding a query for the given letter
    url_parts = list(urlparse.urlparse(url))
    queryobj = dict(urlparse.parse_qsl(url_parts[4]))
    queryobj.update({'q':query})
    url_parts[4] = urllib.urlencode(queryobj)
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
    results = re.findall(pattern, url_text)

    # remove duplicate listings
    if remove_duplicates:
        unique_results = []
        for item in results:
            if item not in unique_results:
                unique_results.append(item)
        results = unique_results

    return results


def get_songs(letters=''):
    '''
    Download and return list of all songs starting with the letters listed in
    the input letters. Default is to use all letters a-z
    '''

    # loop over each letter to construct full songlist
    if not letters:
        letters = tuple(string.ascii_lowercase)

    songlist = []
    print 'Downloading',
    for letter in letters:
        print '%s'%(letter),

        songs = parse_url(query=letter)
        if songs:
            songlist = songlist + songs

    print
    return songlist


def count_list(stringlist, break_words=True):
    '''
    Given a list of strings, return a list of tuples containing each unique
    word or phrase and its number of occurances (ignoring case).
    If break_words is true, then strings are broken into individual words which
    are then compared.
    If break_words if false, strings are not broken into words, and the input
    strings/phrases are compared.
    '''

    # combine all strings and split into a list of words, if requested
    if break_words:
        word_list = re.findall(r"[\w']+", ' '.join(stringlist).lower())
    else:
        word_list = stringlist
    word_dict = {}

    # loop over each word/pharase and either add to the dictionary or increment
    for word in word_list:
        if word not in word_dict:
            word_dict[word] = 1
        else:
            word_dict[word] += 1

    # list of tuples with each word and its number of occurances, sorted by
    # decreasing number of occurances
    word_counts = zip(word_dict.keys(), word_dict.values())
    word_counts = sorted(word_counts, key=lambda x:(x[1], x[0]), reverse=True)

    return word_counts

def print_top(word_counts, title='', num=10):
    '''
    given a list of string-count tuples, print the first ten entries
    '''
    stringlist = []
    ix = 1;

    stringlist.append('==============================')
    stringlist.append('Top %d %s:'%(num, title))
    stringlist.append('------------------------------')
    stringlist.append('#Rank: Occurances Item')
    stringlist.append('==============================')

    if len(word_counts) > num:
        for (word, count) in word_counts[:num]:
            stringlist.append('#%04s: %10s %s'%(str(ix), str(count), str(word)))
            ix += 1
    else:
        for (word, count) in word_counts:
            stringlist.append('#%04s: %10s %s'%(str(ix), str(count), str(word)))
            ix += 1

    fullstring = '\n'.join(stringlist) +'\n'
    print fullstring

    return fullstring

def save_counts(word_counts, filename='word_counts.txt'):
    '''
    Save list of string-count tuples in a text file with the name filename
    '''
    f = open(filename, 'w')
    data = ['%03d %s'%(b,a) for (a,b) in word_counts]
    f.write('\n'.join(data))
    f.close()

def get_release_years(songlist=[], token='', search_type='release', verbose=True):
    '''
    Use Discogs API to get the release year for each (title, artist) tuple
    in the list songlist and return as a list of integer years.

    Notes:
    If the search is unsuccessful, the year is set to be 0.
    The year of the top result is result is returned.
    Discogs API is authenticated using token.
    '''
    if not verbose:
        print 'Working...',

    # read user token if not given
    if not token:
        f = open('discogsapikey')
        token = f.readline()
        f.close()

    # setup the api client
    d = discogs_client.Client('XPN_wordplay/0.1', user_token=token)
    years = []

    # loop over each song title/artist tuple
    for tup in songlist:
        searchstr = ' - '.join(tup)
        try:
            results = d.search(searchstr, type='release')[0]
            if verbose:
                print 'ARTIST: %s'%results.artists[0].name,
                print 'ALBUM: %s'%results.title,
                print 'YEAR: %s'%results.year
            years.append(int(results.year))

        except:
            # if it doesn't work, print a message and return 0 as the year
            warnings.warn('Problem finding year for %s, setting as 0'%searchstr)
            years.append(0)

    if not verbose:
        print 'Done'
    return years

def save_song_info(infolist=[], headerstr=None, pattern='{2:d}\t{0}\t{1}\n',
                   filename='output.txt'):
    '''
    Save the list of info in infolist to the file given by filename using
    pattern to format each item in the list into a string. If headerstr is
    provided, this is inserted at the start of the file
    '''

    f = open(filename, 'w')
    if headerstr:
        f.write(headerstr+'\n')

    for item in infolist:
        f.write(pattern.format(*item))

    f.close()
    return








