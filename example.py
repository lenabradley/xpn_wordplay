'''
Example code to run xpn_wordplay
'''

from wordplay import *

# get list of song titles & artists
songlist = get_songs()

# get song title occurances, title word occurances, and artist occurances
titles = [song[0] for song in songlist]
artists = [song[1] for song in songlist]
title_word_counts = count_words(titles, break_words=True)
title_counts = count_words(titles, break_words=False)
artist_counts = count_words(artists, break_words=False)

# print title, title-word and artists top-ten lists
top_titles = print_top(title_counts, title='titles', num=50)
top_words = print_top(title_word_counts, title='title words', num=50)
top_artists = print_top(artist_counts, title='artists', num=50)

# save top lists to a text file
f = open('top_50_lists.txt', 'w')
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
