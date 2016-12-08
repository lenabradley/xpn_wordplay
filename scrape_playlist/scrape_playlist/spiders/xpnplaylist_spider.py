from scrapy.http import FormRequest
from scrapy.spiders import Spider
import re
import urllib
import urlparse
import pandas as pd
import datetime as dt
import os
import glob
#from scrapy.utils.response import open_in_browser


# hard code start time and the number of days to search
timezero = dt.datetime(2016, 11, 30, 6, 0)
num_days = 10

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
            match = re.search(r'(\d\d)\:(\d\d) ([ap])m ([^-]+) - ([^-]+)', text)
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
                artist = match.group(4)
                track = match.group(5)
                textOK = True

            # parse link address for album name
            # 1) extract query string which contains the song info
            # 2) parse the query string to extract the album name
            link = urllib.unquote(link)
            link = urlparse.urlparse(link)
            qstr = ''
            if link.query:
                link_qs = urlparse.parse_qs(link.query)
                try:
                    qstr = link_qs['q'][0]
                except:
                    None

            match = re.search(r'\^([^\^]+)\^\d+$', qstr)
            if match:
                album = match.group(1)
                linkOK = True;

            # store all data
            if dateOK and textOK and linkOK:
                songtime = dt.datetime(year, month, day, hour, minute)
                # skip if before the 'zero' time when A-Z started
                if songtime > timezero:
                    songtimes.append(songtime)
                    artists.append(artist)
                    albums.append(album)
                    tracks.append(track)

        # store data in dataframes
        df = pd.DataFrame({'time':songtimes[::-1], 'artist':artists[::-1],
                           'album':albums[::-1], 'track':tracks[::-1]})

        # save as tab-delimited data
        filename = 'playlistdata_{0:04d}_{1:02d}_{2:02d}.csv'.format(year, month, day)
        filename = os.path.abspath(filename)
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

    def closed(self, response):
        '''
        import data saved by the scrapy spider
        concatenate data from all days and save as a pandas DataFrame
        '''

        # import all data
        paths = glob.glob('playlistdata_*.csv')
        dflist = []
        for filename in paths:
            dflist.append(pd.read_csv(filename, sep='\t', header=0))

        # concatenate data from each file/day
        data = pd.concat(dflist, ignore_index=True)

        # save as master data csv
        filename = os.path.abspath('D:\\Users\\Lena\\Documents\\projects\\xpn_wordplay\\playlistdata.csv')
        data.to_csv(filename, sep='\t', encoding='utf-8', index=False)

        print '*** Saved master data to {0}'.format(filename)


