'''
Download and display stats about WXPN's A-Z songs playlist
'''

# imports
import urllib
import urlparse
import re
import string

# function definitions
def url_songs(url='http://origin.xpn.org/static/az.php', letter='a',
                  pattern=r'<li>([^<]+) - ([^<]+)</li>', remove_duplicates=True):
    '''
    Download data from the provided url, querying for all songs that start with
    the given letter and return a list of songs. Url text is parsed using the
    regular expression given in pattern.
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

    # remove duplicate listings
    if remove_duplicates:
        unique_songs = []
        for song in songs:
            if song not in unique_songs:
                unique_songs.append(song)
        songs = unique_songs

    return songs


def get_songs():
    '''
    Download and return list of all songs a-z
    '''

    # loop over each letter to construct full songlist
    letters = tuple(string.ascii_lowercase)
    songlist = []
    print 'Downloading',
    for letter in letters:
        print '%s'%(letter),

        songs = url_songs(letter=letter)
        if songs:
            songlist = songlist + songs

    print
    return songlist


def count_words(stringlist, break_words=True):
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
    word_counts = sorted(word_counts, key=lambda x: x[1], reverse=True)

    return word_counts

def print_top(word_counts, title='', num=10):
    '''
    given a list of string-count tuples, print the first ten entries
    '''

    print '========================='
    print 'Top %d %s:'%(num, title)
    print '========================='

    ix = 1

    if len(word_counts) > num:
        for (word, count) in word_counts[:num]:
            print '#%d: %03d %s'%(ix, count, word)
            ix += 1
    else:
        for (word, count) in word_counts:
            print '#%d: %03d %s'%(ix, count, word)
            ix += 1


def save_counts(word_counts, filename='word_counts.txt'):
    '''
    Save list of string-count tuples in a text file with the name filename
    '''
    f = open(filename, 'w')
    data = ['%03d %s'%(b,a) for (a,b) in word_counts]
    f.write('\n'.join(data))
    f.close()



















