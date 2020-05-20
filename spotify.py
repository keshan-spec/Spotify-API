import sys
import spotipy
import spotipy.util as util
import json
import webbrowser, requests
from bs4 import BeautifulSoup


class SpotifyApi:
    def __init__(self, username, client_id, client_secret, redirect_uri="http://localhost:8888/callback/"):
        self.username = username
        self.my_playlists = []
        self.track_list = []
        try:
            self.token = util.prompt_for_user_token(self.username, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
            if self.token:
                self.sp = spotipy.Spotify(auth=self.token)
            else:
                print(f"Can't get token for {self.username}")
                return
        except Exception:
            exit()

    def get_tracks(self, tracks):
        for item in tracks['items']:
            track = item['track']
            self.track_list.append({
                "artist":track['artists'][0]['name'],
                "track": track['name'].replace('"',''),
                "url":track['external_urls']['spotify']
            })
        return self.track_list

    def get_my_playlists(self):
        playlists = self.sp.user_playlists(self.username)
        for playlist in playlists['items']:
            if playlist['owner']['id'] == self.username:
                results = self.sp.playlist(playlist['id'], fields="tracks,next")
                self.my_playlists.append({
                    'playlist': playlist['name'],
                    'url': playlist['external_urls']['spotify'],
                    'total_tracks': playlist['tracks']['total'],
                    'tracks': self.get_tracks(results['tracks'])
            })
        return self.my_playlists
        
    def print(self, string):
        print(json.dumps(string, indent=2))

    def search(self, q, type='track', limit=5):
        artist = {}
        try:
            res = self.sp.search(q=q, type=type, limit=limit)
            for idx, item in enumerate(res[type+'s']['items']):
                if type in ['album', 'track']:
                    artist[idx] = [item['uri'], item['name'], item['external_urls']
                                        ['spotify'], item['artists'][0]['name']]
                else:
                    artist[idx] = [item['uri'], item['name'],
                                   item['external_urls']['spotify']]
            return artist
        except Exception as e:
            print(e)
            return


if __name__ == '__main__':
    with open('.SECRET', 'r') as f:
        username, client, secret = map(lambda key: key.strip().split("=")[1], f.readlines())

    api = SpotifyApi(username, client_id=client, client_secret=secret)
    my_playlists = api.get_my_playlists()
    
    query, type_ = None, None
    types = ['playlist', 'track', 'show', 'album', 'artist']
    print(f"TYPES {types}")
    while not all([query, type_]):
        query = input("Search for > ") if not query else query
        type_ = input("Type > ")
        if type_.lower() not in types:
            print("Invalid type!")
            type_ = None


    q = api.search(query, type_)
    api.print(q)

    # webbrowser.open(url=q[0][2])
    # r = requests.get(q[0][2])
    # soup = BeautifulSoup(r.content, 'html.parser')
    # print(soup.title)
    # print(soup.find(title="Play"))
