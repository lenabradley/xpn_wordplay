'''
Functions to download and display stats about WXPN's A-Z songs playlist

Author: Lena Bartell, github.com/lbartell
'''

# imports
import urllib
import urllib2
import urlparse
import re
import string
import discogs_client
import warnings
import pandas as pd
import glob


# function definitions
def read_data():
    '''
    import data saved by the scrapy spider
    concatenate data from all days and return as a pandas DataFrame
    '''

    # import all data
    paths = glob.glob('playlistdata_*.csv')
    dflist = []
    for filename in paths:
        dflist.append(pd.read_csv(filename, sep='\t', header=0))

    # concatenate data from each file/day
    data = pd.concat(dflist, ignore_index=True)

    return data


def get_discogs_data(songlist=[], token='', search_type='release', verbose=True):
    '''
    Use Discogs search to get more data for each (artist, album, track)
    tuple in the list songlist. Return corresponding lists of release year,
    genres, and album titles.

    Notes:
    Each track may be associated with multiple genres (stored as a list).
    If the search is unsuccessful, the data is set to [] .
    The year of the first result is returned.
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
    genres = []
    albums = []

    # loop over each song title/artist tuple
    for tup in songlist:
        artist, _, track = tup
        results = d.search(type='master',
                           artist=artist, track=track, sort='year,desc') # **** sorting not working.. why?!?
        results = results.sort(u'year')
        if results:
            release = results[0].main_release
            year = release.year
            genre = release.genres
            album = release.title
            if verbose:
                print 'YEAR: %s'%year
                print 'ARTIST: %s'%artist
                print 'TRACK: %s'%track
            years.append(year)
            genres.append(genre)
            albums.append(album)

        else:
            # if it doesn't work, print a message and return 0 as the year
            warnings.warn('* Problem finding track %s - %s - %s, setting as empty'%(tup))
            years.append([])
            genres.append([])
            albums.append([])

    if not verbose:
        print 'Done'

    return (years, genres, albums)



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
    given a list of string-count tuples, print the first num entries
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








