# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 17:51:12 2016

@author: Lena
"""
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
from scrapy.selector import Selector

# read url
url = 'http://xpn.org/playlists/xpn-playlist'
f = urllib.urlopen(url)
text = f.read()
f.close()
hreflist = Selector(text=text).xpath('//div[@id="accordion"]/h3/a/@href').extract()

# pares response
for link in hreflist:
#    link = urllib.unquote(link)
    link = urlparse.urlparse(link)

    if link.query:
        link_qs = urlparse.parse_qs(link.query)
#        link_qs = urllib.unquote(link_qs)
        qstr = link_qs['q'][0]
        match = re.search(r'([^\^]+)\^([^\^]+)\^([^\^]+)\^\d+$', qstr)

        if match:
            artist = match.group(1)
            track = match.group(2)
            album = match.group(3)
        else:
            artist = []
            track = []
            album = []

    print '{0} by {1} on {2}'.format(track, artist, album)
