'''
Code to run xpn_wordplay to download, save, and analyze XPN A-Z playlist data

Author: Lena Bartell, github.com/lbartell
'''
from wordplay import *

## Gather all song data
data = read_data()
artists = list(data['artist'])
times = list(data['time'])
tracks = list(data['track'])
albums = list(data['album'])

## Analyze all song data & save results

# calculate and save title, title-word and artists top-ten lists
title_word_counts = count_list(tracks, break_words=True)
title_counts = count_list(tracks, break_words=False)
artist_counts = count_list(artists, break_words=False)

top_words = print_top(title_word_counts, title='title words', num=50)
top_titles = print_top(title_counts, title='titles', num=50)
top_artists = print_top(artist_counts, title='artists', num=50)

# save top lists to a text file
f = open('last_updated.txt')
nowstr = f.readline()
f.close()
f = open('top_50_lists.txt', 'w')
f.write('WXPN A to Z analysis #XPNAtoZ www.xpn.org, by Lena Bartell\n')
f.write(nowstr)
f.write('\n\n')
f.write(top_artists)
f.write('\n')
f.write(top_titles)
f.write('\n')
f.write(top_words)
f.close()

# save title, title-word and artists counts
save_counts(title_counts, filename='top_titles.txt')
save_counts(title_word_counts, filename='top_title_words.txt')
save_counts(artist_counts, filename='top_artists.txt')










