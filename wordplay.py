"""
Functions to download and display stats about WXPN's A-Z songs playlist

Author: Lena Bartell, github.com/lbartell
"""
# imports
import re
import warnings
import pandas as pd
import os
import string
import musicbrainzngs as mb
import datetime as dt
import glob
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'

# function definitions
def read_playlist_data(filename=None, update_mb=False, save_data=True):
    '''
    import data saved by the scrapy spider, update the musicbrainz data,
    re-save the data, and return the data as a pandas DataFrame

    release_year key:
    if 0: haven't looked for this track yet (new data)
    if 1: failed to find this track before (don't try again)
    '''

    # setup for import
    col_dtypes = {'artist':str, 'track':str, 'time':dt.datetime, 'release_year':np.int64}
    csv_kwargs = {'sep': '\t', 'header': 0, 'dtype': col_dtypes, 'index_col':'time'}

    # import all raw data & remove duplicates
    paths = glob.glob('./scrape_playlist/playlistdata_*.csv')
    dflist = []
    for path in paths:
        dflist.append(pd.read_csv(path, **csv_kwargs))
    raw_data = pd.concat(dflist)
    raw_data = raw_data.drop_duplicates().reset_index()

    # import all current data & remove duplicates
    if filename is None:
        filename = 'playlistdata.csv'
    filename = os.path.abspath(filename)
    prev_data = pd.read_csv(filename, **csv_kwargs)
    prev_data = prev_data.drop_duplicates().reset_index()

    # combine into master dataframe & fill NaNs with zeros
    data = prev_data.merge(raw_data, how='outer')
    data = data.fillna(value=int(0))
    data['release_year'] = data['release_year'].astype(np.int64)

    # save data
    to_csv_kwargs = {'sep':'\t', 'encoding':'utf-8', 'index':False}
    if save_data:
        data.to_csv(filename, **to_csv_kwargs)
        print 'data - combined raw and prev data and saved to: {0}'.format(filename)

    # update musicbrainz data
    if (not data.empty) and update_mb:
        letters = list(string.ascii_lowercase)

        # update one letter at a time, saving in between
        for letter in letters:

            # get MB data for the current subset
            keep = [x[0].lower()==letter for x in data['track']]
            sub_data = data.loc[keep]
            sub_data = get_mb_data(sub_data)

            # append it to the full dataset and save
            data[keep] = sub_data
            data.to_csv(filename, **to_csv_kwargs)
            print 'data - update MB data for {0} and saved to: {1}'.format(letter, filename)

    return data


def get_mb_data(data):
    '''
    Given pandas dataframe containing song information, fill in data about
    release year, album, etc, for entires that don't yet have that info. Return
    the completed table
    '''

    # setup musicbrainz agent
    filename = 'contact'
    filename = os.path.abspath(filename)
    f = open(filename, 'r')
    contact = f.read()
    f.close()
    mb.set_useragent('xpn playlist analysis', '1.0', contact=contact)

    # setup output
    years = []

    # run search on each song
    for song in data.itertuples():

        # only run the search if we don't have the data already
        if (song.release_year is None) or (song.release_year==0):

            query = 'artist:"{0}" AND recording:"{1}" AND status:"official"'.format(song.artist, song.track)
            results = mb.search_recordings(query=query, strict=True)

            # extract fields of interest
            release_year, _ = extract_mb_results(results)

            # show result
            try:
                print '{0:d} {1} by {2}'.format(release_year, song.track, song.artist)
            except:
                print 'error', release_year, 'setting to 1'
                release_year = 1

            years.append(release_year)

        else:
            release_year = int(song.release_year)
            years.append(release_year)

    # update dataframe
    data.loc[:,'release_year'] = years

    # return data frame
    return data

def extract_mb_results(results):
    '''
    given results from a musicbrainzngs.search_recordings query, extract the
    earliest official release and return the year and album name. If no
    results, return year as 1 and album name as ''
    '''

    # extract all release years
    alldata = []
    if 'recording-list' in results:
        recording_list = results['recording-list']
        for rec in recording_list:

            if 'release-list' in rec:
                release_list = rec['release-list']

                for rel in release_list:

                    # get album name
                    if 'title' in rel:
                        title = rel['title']
                    else:
                        title = []

                    # get album release year
                    if 'date' in rel:
                        match = re.search(r'\d\d\d\d', rel['date'])
                        if match:
                            year = int(match.group())
                        else:
                            year = []
                    else:
                        year = []

                    # store data
                    alldata.append((year, title))

    # identify earliest matching release
    if alldata:
        data = min(alldata, key=lambda x: x[0])
    else:
        data = (1, '')

    return data

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

def save_counts(word_counts, filename='counts.txt'):
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

    # gather song data and update MB info
    filename = 'playlistdata.csv'
    data = read_playlist_data(filename=filename, update_mb=True, save_data=True)
    artists = list(data['artist'])
    years = list(data['release_year'])
    tracks = list(data['track'])
    first_word = [x.split()[0] for x in tracks]
    albums = list(data['album'])
    times = pd.to_datetime(data['time']).tolist()

    # count unique artists, titles, and title words
    unique_track_words = count_list(tracks, break_words=True)
    unique_tracks = count_list(tracks, break_words=False)
    unique_artists = count_list(artists, break_words=False)
    unique_years = count_list(years, break_words=False)
    unique_first_word = count_list(first_word, break_words=False)

    # save title, title-word and artists counts
    save_counts(unique_track_words, filename='top_title_words.txt')
    save_counts(unique_tracks, filename='top_titles.txt')
    save_counts(unique_artists, filename='top_artists.txt')
    save_counts(unique_years, filename='top_years.txt')
    save_counts(unique_first_word, filename='top_first_word.txt')

    # get top 20 lists
    top_track_words = print_top(unique_track_words, title='title words', num=50, quiet=True)
    top_tracks = print_top(unique_tracks, title='titles', num=50, quiet=True)
    top_artists = print_top(unique_artists, title='artists', num=50, quiet=True)
    top_years = print_top(unique_years, title='release year', num=50, quiet=True)

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
    f.write('\n')
    f.write(top_years)
    f.close()

    # Number of tracks in each letter
    first_letter = [x[0].lower() for x in tracks]
    letter_counts = dict((x,0) for x in list(string.ascii_lowercase))
    unique_letters = count_list(first_letter, break_words=False)
    letter_counts.update(unique_letters)
    unique_letters = zip(letter_counts.keys(), letter_counts.values())
    save_counts(unique_letters, filename='letter_counts.txt')

    # text file listing totals of interest
    letters_played = len([x[0] for x in unique_letters if x[1]>0])
    pct_played = letters_played / 26. * 100.
    letters_played_str = '{0:d} ({1:04.1f}%)'.format(letters_played, pct_played)
    elapsed = max(times)-min(times)
    f = open(os.path.abspath('summary.txt'),'w')
    f.write('{0}:\t{1}\n'.format('Elapsed time', str(elapsed)))
    f.write('{0}:\t{1}\n'.format('Songs', len(tracks)))
    f.write('{0}:\t{1}\n'.format('Artists', len(unique_artists)))
    f.write('{0}:\t{1}\n'.format('Song Titles', len(unique_tracks)))
    f.write('{0}:\t{1}\n'.format('Song Title Words', len(unique_track_words)))
    f.write('{0}:\t{1}\n'.format('Letters', letters_played_str))
    f.close()



if __name__ == '__main__':
  main()

