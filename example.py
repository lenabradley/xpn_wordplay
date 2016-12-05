'''
Code to run xpn_wordplay to download, save, and analyze XPN A-Z playlist data

Author: Lena Bartell, github.com/lbartell
'''

from wordplay import *
import datetime
import string
import os
import csv

## ====================
## Gather all song data
## ====================
letters = tuple('abcdefg') #letters = tuple(string.ascii_lowercase)
full_songlist = []

# gather data from all letters
for letter in letters:
    datafilename = letter+'_data.txt'

    # see if the data file already exists
    if os.path.isfile(datafilename):
        # if yes, import it

        with open(datafilename, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                row[0] = int(row[0])
                full_songlist.append(tuple((row[1], row[2], row[0])))

    else:
        # otherwise, gather and save data from the associated letter

        # get song titles and artists and release year
        songlist = get_songs(letters=letter)
        years = get_release_years(songlist=songlist)
        titles = [x[0] for x in songlist]
        artists = [x[1] for x in songlist]
        songlist = zip(titles, artists, years)

        # save the data
        save_song_info(infolist=songlist, filename=datafilename)

        # add data for full list
        full_songlist += songlist

## ====================================
## Analyze all song data & save results
## ====================================

all_titles = [x[0] for x in full_songlist]
all_artists = [x[1] for x in full_songlist]
all_years = [x[2] for x in full_songlist]

# calculate and save title, title-word and artists top-ten lists
title_word_counts = count_list(all_titles, break_words=True)
title_counts = count_list(all_titles, break_words=False)
artist_counts = count_list(all_artists, break_words=False)
year_counts = count_list(all_years, break_words=False)

top_words = print_top(title_word_counts, title='title words', num=50)
top_titles = print_top(title_counts, title='titles', num=50)
top_artists = print_top(artist_counts, title='artists', num=50)
top_years = print_top(year_counts, title='release years', num=50)

# save top lists to a text file
now = datetime.datetime.now()
nowstr = 'Last updated: %04d-%02d-%02d, %02d:%02d'%(now.year, now.month, now.day,
                                                   now.hour, now.minute)
f = open('top_50_lists.txt', 'w')
f.write('WXPN A to Z analysis #XPNAtoZ www.xpn.org, by Lena Bartell\n')
f.write(nowstr)
f.write('\n\n')
f.write(top_artists)
f.write('\n')
f.write(top_titles)
f.write('\n')
f.write(top_words)
f.write('\n')
f.write(top_years)
f.close()

# save title, title-word and artists counts
save_counts(title_counts, filename='top_titles.txt')
save_counts(title_word_counts, filename='top_title_words.txt')
save_counts(artist_counts, filename='top_artists.txt')
save_counts(year_counts, filename='top_artists.txt')











