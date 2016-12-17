'''
When will the XPN A to Z end?! Lets try to guess
'''
# imports
from xpn_wordplay import wordplay as wp
import pandas as pd
import string
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import datetime as dt

# function defs
def organize_tracks(data):
    '''
    Gather track data by first letter and return a list of the number of songs
    in each letter
    '''

    # get unique names only, capitalize 1st letter, and sort alphabetically
    tracks = list(data['track'])
    tracks = set(tracks)
    tracks = [x[0].upper()+x[1:] for x in tracks]
    tracks = sorted(tracks)

    # measure number of tracks in each letter
    count = []
    letters = list(string.ascii_uppercase)
    for letter in letters:
        letter_sum = sum([x[0] == letter for x in tracks])
        count.append((letter, letter_sum))

    res = [x for (letter, x) in count]

    return res

def compare_counts(lookback, atoz):

    letters = list(string.ascii_uppercase)[:20] # use data through "T"


'''
Run analysis
'''


# import & count historical playlist data
filename = 'lookback_playlistdata.csv'
lookback_data = wp.read_playlist_data(filename=filename, rawglob='./scrape_playlist/lookback/playlistdata_*.csv',
                          update_mb=False, save_data=True)
lookback_count = organize_tracks(lookback_data)


# import & count current data
data = wp.read_playlist_data(update_mb=False, save_data=False)
atoz_count = organize_tracks(data)

# Compare data & fit to a line
letters = list(string.ascii_uppercase)
xdata = lookback_count[:20]
ydata = atoz_count[:20]
pfit = np.polyfit(xdata, ydata, 1)
xfit = range(min(xdata), max(xdata), 10)
yfit = np.polyval(pfit, xfit)


# plot lookback vs atoz data ==> Looks linear, good!
font = {'family' : 'sans',
        'weight' : 'normal',
        'size'   : 16}
matplotlib.rc('font', **font)
labels = ['{0}'.format(x) for x in letters[:20]]
plt.scatter(xdata, ydata, s=20, marker='*', color='k') # plot raw data
for (text, x, y) in zip(letters, xdata, ydata): # annotate each point
    plt.annotate(s=text, xy=(x+10,y+10), size=12)
plt.plot(xfit, yfit, 'b-', label='Linear Fit [{0:0.4f}, {1:0.4f}]'.format(*tuple(pfit))) #linear fit line


for (text, x, y) in zip(letters[20:24], lookback_count[20:24], atoz_count[20:24]):
    plt.plot(x, y, 'r*', ms=20)
    plt.annotate(s=text, xy=(x+10, y+10), size=18, color='r')

plt.xlabel('Historical playlist count (# songs)')
plt.ylabel('A to Z playlist count (# songs)')
plt.xlim([0, 800])
plt.ylim([0, 700])
ax = plt.gca()
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels, bbox_to_anchor=(0.8, 1))
plt.savefig('historical_fit.png')
plt.show()

# get predictions for remaining letters
lookback = dict(zip(letters, lookback_count))
atoz = dict(zip(letters, atoz_count))
numleft = 0
for letter in letters[20:]:
    nsongs = int(round(np.polyval(pfit, lookback[letter])))
    if nsongs < 0:
        nsongs = 0
    atoz[letter] = nsongs
    print 'Prediction: {0} will have {1:d} songs'.format(letter, atoz[letter])
    numleft += nsongs

print 'Number of songs remaining:', numleft


# how long will the reamining songs take?
dt_Tend = dt.datetime(2016, 12, 15, 14, 4)
avg_rate = 13.75 / 3600. # songs per second
sec_left = numleft / avg_rate
dt_left = dt.timedelta(seconds=sec_left) # time remaining (after T ended)
end_time = dt_Tend + dt_left
print 'Predicted end time:', end_time
end_time2 = end_time + dt.timedelta(seconds=60.*45)
print 'Modified Predicted end time:', end_time2

# modify prediction
numleft = int(round(numleft * 1.02))
print 'Modified Number of songs remaining (*1.02):', numleft
dt_Tend = dt.datetime(2016, 12, 15, 14, 4)
avg_rate = 13.75 / 3600. # songs per second
sec_left = numleft / avg_rate
dt_left = dt.timedelta(seconds=sec_left) # time remaining (after T ended)
end_time = dt_Tend + dt_left
print 'Modified Predicted end time (*1.02):', end_time

# modify for the Friday concert
end_time = end_time + dt.timedelta(seconds=60.*45)
print 'Modified Predicted end time (*1.02 & +45 for free at noon):', end_time








