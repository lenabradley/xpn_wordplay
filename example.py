'''
Example code to test xpn_wordplay
'''

from wordplay import *

# get list of song titles & artists
songlist = get_songs()

# print songlist
num_songs = len(songlist)
if num_songs <=10:
    for song in songlist:
        print '%s - %s'%(song)
else:
    for song in songlist[:5]:
        print '%s - %s'%(song)
    print '...'
    for song in songlist[-5:]:
        print '%s - %s'%(song)
print 'Total number of songs: %d'%num_songs

# get song title occurances, title word occurances, and artist occurances
titles = [song[0] for song in songlist]
artists = [song[1] for song in songlist]
title_word_counts = count_words(titles, break_words=True)
title_counts = count_words(titles, break_words=False)
artist_counts = count_words(artists, break_words=False)

# print title, title-word and artists top-ten lists
print_top(title_counts, title='titles')
print_top(title_word_counts, title='title words')
print_top(artist_counts, title='artists')

save_counts(title_counts, filename='title_counts.txt')
save_counts(title_word_counts, filename='title_word_counts.txt')
save_counts(artist_counts, filename='artist_counts')
