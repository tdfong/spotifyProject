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
copy and paste these into terminal

export SPOTIPY_CLIENT_ID='9d4a61375f944aa881655352c3d57461'
export SPOTIPY_CLIENT_SECRET='29abc791076e4fb395147c5405d691d3'
export SPOTIPY_REDIRECT_URI='http://yahoo.com/'
'''

userID = 'gfz5t2fe5eupt9d287cmn2cf4'
scope = '''user-read-private
        playlist-modify-private
        playlist-modify-public
        playlist-read-private
        user-library-read
        user-top-read
        user-read-recently-played
        user-read-playback-state
        user-modify-playback-state'''

try:
    token = util.prompt_for_user_token(userID, scope)
except:
    os.remove(f".cache-{userID}")
    token = util.prompt_for_user_token(userID, scope)

spotifyObject = spotipy.Spotify(auth=token)
user = spotifyObject.current_user()

#DEVICES
devices = spotifyObject.devices()
deviceID = devices['devices'][0]['id']

#print(json.dumps(user, sort_keys=True, indent=4))

displayName = user['display_name']
followers = user['followers']['total']

def show_tracks(tracks, index=0):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        print("   %d %32.32s %s" % (i+index, track['artists'][0]['name'], track['name']))

def all_tracks(tracks, specific_category=None): #stores track objects from a tracks object
    savedTracks = []
    while tracks:
        savedTracks += [track for track in tracks['items']]
        if tracks['next']:
            tracks = spotifyObject.next(tracks)
        else:
            tracks = None
    if specific_category:
        savedTracks = [track['track'][specific_category] for track in savedTracks]

    return savedTracks


#print(dir(spotipy.Spotify))

print("\nWelcome to Spotipy " + displayName + "!")
print("You have " + str(followers) + " followers.")

#STORING ALL PLAYLISTS
allPlaylists = []
playlistsObject = spotifyObject.user_playlists('gfz5t2fe5eupt9d287cmn2cf4')
while playlistsObject:
    allPlaylists += [(i+1+playlistsObject['offset'], playlist) for i,playlist in enumerate(playlistsObject['items'])]
    if playlistsObject['next']:
        playlistsObject = spotifyObject.next(playlistsObject)
    else:
        playlistsObject = None


timeOfCapture = datetime.datetime.now()

#Date as INT helper function for individual date
def dateToIntConverter(string):
    use_year, use_month, use_day, use_hour, use_minute, use_sec = (float(string[0:4]),
                                                        float(string[5:7]),
                                                        float(string[8:10]),
                                                        float(string[11:13]),
                                                        float(string[14:16]),
                                                        float(string[17:]))
    return use_year*365 + use_month*30 + use_day + (use_hour + use_minute/60 + use_sec/(60**2))/24

while True:
    print()
    print('''------MAIN MENU------

        Input 0 to search for an artist,
        1 to look at your playlists,
        2 to view your most recently played song,
        3 to view your top songs,
        4 to view your top artists,
        5 to view your entire saved library,
        or EXIT to exit: ''')
    choice = input("Your choice: ")

    #search for the artist:
    if choice=='0':
        print()
        searchQuery = input("artist name: ")
        print()

        #get search results
        searchReults = spotifyObject.search(searchQuery, 1, 0, 'artist')
        print(json.dumps(searchReults, sort_keys=True, indent=4))

    if choice=='1':
        howMany = input('\nWould you like to look at one or all playlists? \n1 or ALL: ')

        if str.isnumeric(howMany) & (howMany=='1'):
            whichPlaylist = input("\nChoose a playlist index to see all tracks: \n")
            if str.isnumeric(whichPlaylist):
                whichPlaylist = int(whichPlaylist)

                playlist = spotifyObject.user_playlists('gfz5t2fe5eupt9d287cmn2cf4', offset=whichPlaylist-1, limit=1)['items'][0]
                print("\nPlaylist name: " + str.upper(playlist['name']))
                results = spotifyObject.user_playlist(userID, playlist['id'], fields="tracks,next")
                tracks = results['tracks']
                show_tracks(tracks)

        if howMany=="ALL":
            for i, playlist in allPlaylists:
                print("%4d %s" % (i, str.upper(playlist['name'])))

            '''playlists = spotifyObject.user_playlists('gfz5t2fe5eupt9d287cmn2cf4')
            while playlists:
                for i, playlist in enumerate(playlists['items']):
                    print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'], str.upper(playlist['name'])))
                if playlists['next']:
                    playlists = spotifyObject.next(playlists)
                else:
                    playlists = None'''

    if choice=='2':
        print("\n------MOST RECENTLY PLAYED SONG------\n")
        listeningHistory = spotifyObject.current_user_recently_played()

        allArtists = []
        for artist1 in listeningHistory['items'][0]['track']['album']['artists']:
            allArtists.append(artist1['name'])
        print(listeningHistory['items'][0]['track']['name'] + " by " + str(allArtists))

    if choice=='3':
        numSongs = int(input('How many of your top songs do you want to see? '))
        print('\nNow calculating your top ' + str(numSongs) + ' songs...\n')

        topSongs, numTimes = [], tuple(zip([50]*(numSongs//50) + [numSongs%50], np.arange(0, numSongs, 50)))
        #only allows 50 songs for now, hopefully will go up in the future
        for lim, off in numTimes:
            topSongsTemp = spotifyObject.current_user_top_tracks(limit=lim, offset=off, time_range='long_term')
            topSongs += [topSongsTemp['items'][i] for i in np.arange(lim)]

        topSongsCopy = topSongs.copy()
        for i, item in enumerate(topSongs):
            allArtists = []
            for artist1 in item['artists']:
                allArtists.append(artist1['name'])
            print("   %d %32.32s %s" % (i+1, item['name'], str(allArtists)))

        favsPlaylist = [i[1] for i in allPlaylists if i[1]['name']=='favs'][0]
        favsPlaylistID = favsPlaylist['id']

        favsPlaylistTracks = all_tracks(spotifyObject.user_playlist(userID, playlist_id=favsPlaylistID)['tracks'], 'id')
        topSongIDs = [song['id'] for song in topSongs]
        topSongIDNoRepeats = [id for id in topSongIDs if id not in favsPlaylistTracks]
        #prevent overlap

        for id in topSongIDNoRepeats:
            spotifyObject.user_playlist_add_tracks(userID, favsPlaylistID, topSongIDNoRepeats)

        print('\nSuccessfully added ' + str(len(topSongIDNoRepeats)) + ' of your top songs to your FAVS playlist.\n')

        saveProgress = input('\nWould you like to track these songs? Y or N: ')

        if saveProgress=='Y':
            #topPersonalSongs = None
            topPersonalSongsIDs, topPersonalSongsNames = [], []
            try:
                writer = pd.ExcelWriter(displayName + "'s TOP SONGS EXCEL.xlsx", engine='xlsxwriter')

                #topPersonalSongs = pd.read_excel(displayName + "'s TOP SONGS EXCEL.xlsx")
                #topPersonalSongs = topPersonalSongs.drop(topPersonalSongs.columns[[0]], axis=1)

                topPersonalSongsIDs = pd.read_excel(displayName + "'s TOP SONGS EXCEL.xlsx", index_col=0, sheet_name='IDs')
                topPersonalSongsIDs[str(timeOfCapture)] = topSongIDs
                topPersonalSongsIDs.to_excel(writer, sheet_name='IDs')

                topPersonalSongsNames = pd.read_excel(displayName + "'s TOP SONGS EXCEL.xlsx", index_col=0, sheet_name='Names')
                topPersonalSongsNames[str(timeOfCapture)] = [song['name'] for song in topSongsCopy]
                topPersonalSongsNames.to_excel(writer, sheet_name='Names')

                writer.save()

                print('\nSuccessfully updated top songs EXCEL.')
            except:
                SOMETHINGSWRONG
                topPersonalSongs = pd.DataFrame(data={str(timeOfCapture):tuple(zip([song['name'] for song in topSongsCopy], topSongIDs))})
                topPersonalSongs.to_excel(displayName + "'s TOP SONGS EXCEL.xlsx")
                print('\nSuccessfully created new top songs EXCEL.')

            showGraph = input('\nWould you like to see the top songs line graph? Y or N: ')
            if showGraph=='Y':
                #print(list(topPersonalSongs.columns))
                uniqueSongs = np.unique(topPersonalSongsIDs)

                f = plt.figure()
                dateAsInt = [dateToIntConverter(date) for date in topPersonalSongsIDs.columns]
                for time in topPersonalSongs:

                    plt.plot(dateAsInt, data=topPersonalSongs, marker='o', markersize=4)
                plt.title(displayName + "'s TOP SONGS")
                plt.xlabel('Duration between data collection in Days')
                plt.ylabel()
                plt.legend()
                pp.savefig(f)

    if choice=='4':
        numArtists = int(input('How many of your top artists do you want to see? '))
        print('\nNow calculating your top artists...\n')

        topArtistsTemp = spotifyObject.current_user_top_artists(limit=numArtists, time_range='long_term')
        topArtists = [topArtistsTemp['items'][i] for i in np.arange(numArtists)]

        topSongsTemp = spotifyObject.current_user_top_tracks(limit=50, time_range='long_term')
        topSongs = [topSongsTemp['items'][i] for i in np.arange(50)]

        for i, item in enumerate(topArtists):
            artistSongs = []
            for song in topSongs:
                if item['name'] in [song['artists'][i]['name'] for i in np.arange(len(song['artists']))]:
                    artistSongs.append(song['name'])
            print(str(i+1) + "  " + str.upper(item['name']) + " --- " + str(artistSongs))

        saveProgress = input('\nWould you like to track these artists? Y or N: ')

        if saveProgress=='Y':
            try:
                topPersonalArtists = pd.read_excel(displayName + "'s TOP ARTISTS EXCEL.xlsx")[1:]
                topPersonalSongs[str(timeOfCapture)] = tuple(zip([artist['name'] for artist in topArtists], [artist['id'] for artist in topArtists]))
                topPersonalSongs.to_excel(displayName + "'s TOP ARTISTS EXCEL.xlsx")
            except:
                topPersonalSongs = pd.DataFrame(data={str(timeOfCapture):tuple(zip([artist['name'] for artist in topArtists], [artist['id'] for artist in topArtists]))})
                topPersonalSongs.to_excel(displayName + "'s TOP ARTISTS EXCEL.xlsx")

    if choice=='5': #TRY TO SAVE ALL SONGS LOCALLY????
        print("\n------" + str.upper(displayName) + "'s SAVED SONGS------\n")

        allSongs = spotifyObject.current_user_saved_tracks(limit=50)
        #print(allSongs)
        index = 0
        while allSongs:
            show_tracks(allSongs, index)
            if allSongs['next']:
                allSongs = spotifyObject.next(allSongs)
                index += 50
            else:
                allSongs = None

    if choice=='6':
        songName = input("\nWhich song would you like to analyze? ")


    if choice=='EXIT':
        print("\nYou are now exiting the application. Goodbye!\n")
        break























"""['__class__', '__delattr__', '__dict__', '__dir__', '__doc__',
'__eq__', '__format__', '__ge__', '__getattribute__', '__gt__',
'__hash__', '__init__', '__init_subclass__', '__le__', '__lt__',
'__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__',
'__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__',
'__weakref__', '_auth', '_auth_headers', '_delete', '_get', '_get_id',
'_get_uri', '_internal_call', '_post', '_put', '_session', '_warn',
'album', 'album_tracks', 'albums', 'artist', 'artist_albums',
'artist_related_artists', 'artist_top_tracks', 'artists',
'audio_analysis', 'audio_features', 'categories', 'category_playlists',
'client_credentials_manager', 'current_user',
'current_user_followed_artists', 'current_user_playlists',
'current_user_saved_albums', 'current_user_saved_albums_add',
'current_user_saved_tracks', 'current_user_saved_tracks_add',
'current_user_saved_tracks_contains', 'current_user_saved_tracks_delete',
'current_user_top_artists', 'current_user_top_tracks', 'featured_playlists',
'max_get_retries', 'me', 'new_releases', 'next', 'prefix', 'previous', 'proxies',
'recommendation_genre_seeds', 'recommendations', 'requests_timeout', 'search',
'trace', 'trace_out', 'track', 'tracks', 'user', 'user_playlist',
'user_playlist_add_tracks', 'user_playlist_change_details', 'user_playlist_create',
'user_playlist_follow_playlist', 'user_playlist_is_following',
'user_playlist_remove_all_occurrences_of_tracks',
'user_playlist_remove_specific_occurrences_of_tracks',
'user_playlist_reorder_tracks', 'user_playlist_replace_tracks',
'user_playlist_tracks', 'user_playlist_unfollow', 'user_playlists']"""
