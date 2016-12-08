"""
Functions to download and display stats about WXPN's A-Z songs playlist

Author: Lena Bartell, github.com/lbartell
"""
# imports
import re
import discogs_client
import warnings
import pandas as pd
import os
import string
# function definitions

#def get_data():
#
#    # download data from xpn website
#    base_url = 'http://origin.xpn.org/static/az.php'
#    url_parts = list(urlparse.urlparse(base_url))
#
#    # loop over each letter of the alphabet
#    letters = list(string.ascii_letters)
#
#    for letter in letters:
#
#        # format url query
#        url_parts[4] = urllib.urlencode({'q': letter})
#        full_url = urlparse.urlunparse(url_parts)
#
#        # get url data
#        ufile = urllib.urlopen(full_url)
#        url_text = ufile.read()

def read_data(filename=None):
    '''
    import data saved by the scrapy spider, return as a pandas DataFrame
    '''

    # import all data
    if not filename:
        filename = 'D:\\Users\\Lena\\Documents\\projects\\xpn_wordplay\\playlistdata.csv'
    filename = os.path.abspath(filename)
    data = pd.read_csv(filename, sep='\t', header=0)

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

def print_top(word_counts, title='', num=10, quiet=False):
    '''
    given a list of string-count tuples, print the first num entries
    if quiet=True, don't actually print to the screen
    Either way, return a string to print
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
    if not quiet:
        print fullstring

    return fullstring

def save_counts(word_counts, filename='word_counts.txt'):
    '''
    Save list of string-count tuples in a text file with the name filename
    '''
    filename = os.path.abspath(filename)
    f = open(filename, 'w')
    data = ['%03d\t%s'%(b,a) for (a,b) in word_counts]
    f.write('\n'.join(data))
    f.close()

    return None

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


def main():
    '''
    Use contained functions to import, analyze, and save results of xpn
    playlist data
    '''

    # gather song data
    filename = 'D:\\Users\\Lena\\Documents\\projects\\xpn_wordplay\\playlistdata.csv'
    data = read_data(filename=filename)
    artists = list(data['artist'])
    times = list(data['time'])
    tracks = list(data['track'])
    albums = list(data['album'])

    # count unique artists, titles, and title words
    unique_track_words = count_list(tracks, break_words=True)
    unique_tracks = count_list(tracks, break_words=False)
    unique_artists = count_list(artists, break_words=False)

    # save title, title-word and artists counts
    save_counts(unique_track_words, filename='top_title_words.txt')
    save_counts(unique_tracks, filename='top_titles.txt')
    save_counts(unique_artists, filename='top_artists.txt')

    # get top 20 lists
    top_track_words = print_top(unique_track_words, title='title words', num=50, quiet=True)
    top_tracks = print_top(unique_tracks, title='titles', num=50, quiet=True)
    top_artists = print_top(unique_artists, title='artists', num=50, quiet=True)

    # save top 20 lists to a text file
    f = open('last_updated.txt')
    nowstr = f.readline()
    f.close()
    f = open('top_50_lists.txt', 'w')
    f.write('WXPN A to Z analysis #XPNAtoZ www.xpn.org, by Lena Bartell\n')
    f.write(nowstr)
    f.write('\n\n')
    f.write(top_artists)
    f.write('\n')
    f.write(top_tracks)
    f.write('\n')
    f.write(top_track_words)
    f.close()

    # Number of tracks in each letter
    first_letter = [x[0].lower() for x in tracks]
    letter_counts = dict((x,0) for x in list(string.ascii_lowercase))
    unique_letters = count_list(first_letter, break_words=False)
    letter_counts.update(unique_letters)
    unique_letters = zip(letter_counts.keys(), letter_counts.values())
    save_counts(unique_letters, filename='letter_counts.txt')

    # hours per letter


    # number of words in song title




if __name__ == '__main__':
  main()

