import os
import json
import spotipy
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import datetime
import pandas as pd
import matplotlib.pyplot as plt

'''
topPersonalSongs = None
try:
    topPersonalSongs = pd.read_excel("Tim's TOP SONGS EXCEL.xlsx")
    print(topPersonalSongs)
    topPersonalSongs = pd.DataFrame(data={'2019-07-18 01:14:09.655401':[eval(song)[1] for song in topPersonalSongs['2019-07-18 01:14:09.655401']]})
    print(topPersonalSongs)
    topPersonalSongs.to_excel("Tim's TOP SONGS EXCEL.xlsx")
    print('\nSuccessfully updated top songs EXCEL.')
except:
    None
'''
writer = pd.ExcelWriter(displayName + "'s TOP SONGS EXCEL.xlsx", engine='xlsxwriter')

topPersonalSongsIDs = pd.read_excel("Tim's TOP SONGS EXCEL.xlsx", index_col=0, sheet_name='IDs')
topPersonalSongsIDs.to_excel(writer, sheet_name='IDs')

topPersonalSongsNames = pd.read_excel("Tim's TOP SONGS EXCEL.xlsx", index_col=0, sheet_name='Names')
topPersonalSongsNames['2019-07-18 01:14:09.655401'] = []
topPersonalSongsIDs.to_excel(writer, sheet_name='Names')

writer.save()
print('\nSuccessfully updated top songs EXCEL.')
