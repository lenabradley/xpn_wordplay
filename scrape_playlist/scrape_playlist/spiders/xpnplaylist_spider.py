from scrapy.http import FormRequest
from scrapy.spiders import Spider
import re
import urllib
import urlparse
import pandas as pd
import datetime as dt
import os
import glob
from xpn_wordplay import wordplay as wp
import numpy as np
#from scrapy.utils.response import open_in_browser

# hard code start time and the number of days to search
timezero = dt.datetime(2016, 11, 30, 6, 0) # time the A-Z started
now = dt.datetime.now()
endtime = dt.datetime(2016, 12, 17, 13, 26) # time the A-Z ended

# import all current data & remove duplicates
filename = 'D:\\Users\\Lena\\Documents\\projects\\xpn_wordplay\\playlistdata.csv'
filename = os.path.abspath(filename)
col_dtypes = {'artist':str, 'track':str, 'time':dt.datetime, 'release_year':np.int64}
csv_kwargs = {'sep': '\t', 'header': 0, 'dtype': col_dtypes, 'index_col':'time'}
prev_data = pd.read_csv(filename, **csv_kwargs)
prev_data = prev_data.drop_duplicates().reset_index()

## get last song's day
#if not prev_data.empty:
#    start_time_str = max(prev_data['time'])
#    timezero = dt.datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')

# number of days to read
num_days = (endtime-timezero).days+1
print '*** TIME ZERO: ', timezero

class PlaylistSpider(Spider):
    name = "xpn_playlist"
    start_urls = ['http://origin.xpn.org/playlists/xpn-playlist']

    def parse(self, response):
#        open_in_browser(response)

        # setup and loop over each day of interest
        date_list = [timezero + dt.timedelta(days=x) for x in range(0, num_days)]

        for item in date_list:
            datestr = '{0:02d}-{1:02d}-{2:04d}'.format(item.month, item.day, item.year)
            formdata = {'playlistdate': datestr}
            yield FormRequest.from_response(response,
                                            formnumber=2,
                                            formdata=formdata,
                                            callback=self.parse1)

    def parse1(self, response):
        '''
        extract data and save
        '''
        # get xpath results
        datetxt = response.xpath('//h2[@itemprop="headline"]/text()').extract()
        textlist = response.xpath('//div[@id="accordion"]/h3/a/text()').extract()
        hreflist = response.xpath('//div[@id="accordion"]/h3/a/@href').extract()

        # initialize data storage
        songtimes = []
        artists = []
        albums = []
        tracks = []

        # extract date
        match = re.search(r'XPN Playlist for (\d\d)-(\d\d)-(\d\d\d\d)', datetxt[0])
        dateOK = False
        if match:
            year = int(match.group(3))
            month = int(match.group(1))
            day = int(match.group(2))
            dateOK = True

        # extract song info
        for (text,link) in zip(textlist, hreflist):
            textOK = False;
            linkOK = False;

            # parse link text for time, track, and artist info
            match = re.search(r'(\d\d)\:(\d\d) ([ap])m', text)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2))
                meridiem = match.group(3)
                if meridiem == 'p':
                    if hour<12:
                        hour = hour+12
                elif meridiem =='a':
                    if hour==12:
                        hour = hour-12
                textOK = True

            # parse link address for artist, track, and album name
            link = urlparse.urlparse(link)
            if link.query:
                link_qs = urlparse.parse_qs(link.query)
                qstr = link_qs['q'][0]
                match = re.search(r'([^\^]+)\^([^\^]+)\^([^\^]+)\^\d+$', qstr)
                if match:
                    artist = match.group(1)
                    track = match.group(2)
                    album = match.group(3)
                    linkOK = True

                    # manually fix names  ******* obviouslly a pattern here - add regex to fix it!!
                    if artist == 'R. E. M.':
                        artist = 'R.E.M.'
                    elif artist == 'The Eagles':
                        artist = 'Eagles'
                    elif artist == 'J. J. Cale':
                        artist = 'J.J. Cale'
                    elif artist =='k. d. lang':
                        artist = 'k.d. lang'
                    elif artist = 'K. T. Tunstall':
                        artist = 'KT Tunstall'

            # store all data
            if dateOK and textOK and linkOK:
                songtime = dt.datetime(year, month, day, hour, minute)

                # skip if before the 'zero' time
                if (songtime > timezero) and (songtime < endtime):
                    songtimes.append(songtime)
                    artists.append(artist)
                    albums.append(album)
                    tracks.append(track)

        # store data in dataframes, with most recent at the end
        df = pd.DataFrame({'time':songtimes[::-1], 'artist':artists[::-1],
                           'album':albums[::-1], 'track':tracks[::-1]})

        # read in any existing data
        filename = 'playlistdata_{0:04d}_{1:02d}_{2:02d}.csv'.format(year, month, day)
        filename = os.path.abspath(filename)
        if os.path.isfile(filename):
            prev_df = pd.read_csv(filename, sep='\t', header=0)
        else:
            prev_df = pd.DataFrame()

        # combine previous and current data
        df = pd.concat([prev_df, df], ignore_index=True)

        # save as tab-delimited dataframe
        df.to_csv(filename, sep='\t', encoding='utf-8', index=False)
        print 'Saved data to {0}'.format(filename)

        # also save current time as last-updated
        now = dt.datetime.now()
        nowstr = 'Last updated: %04d-%02d-%02d, %02d:%02d'%(now.year, now.month, now.day,
                                                            now.hour, now.minute)
        filename = os.path.abspath('../last_updated.txt')
        f = open(filename, 'w')
        f.write(nowstr+'\n')
        f.close()
        print filename
        print nowstr


