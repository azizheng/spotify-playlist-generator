from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

date = input("What year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}")
website = response.text

soup = BeautifulSoup(website, "html.parser")

title_list = soup.find_all(name="h3", class_="a-no-trucate")
artists = soup.find_all(name="span", class_="a-no-trucate")

song_list = [(title.getText().strip("\n")) for title in title_list]
artists_list = [(artist.getText().strip("\n")) for artist in artists]

SPOTIPY_CLIENT_ID = os.environ["SPOTIPY_CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]
SPOTIPY_REDIRECT_URI = os.environ["SPOTIPY_REDIRECT_URI"]

scope = "playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI, scope=scope, cache_path="token.txt"))
results = sp.current_user()

song_uri_list = []
index = 0

for _ in song_list:
    try:
        uri = sp.search(q=f"track:{song_list[index]} artist:{artists_list[index]}", type="track")
        song_uri_list.append(uri["tracks"]["items"][0]["uri"])
    except IndexError:
        print(f"{song_list[index]} by {artists_list[index]} does not exist in Spotify")
    index += 1

playlist_info = sp.user_playlist_create(user=results["id"], name=f"{date} 100 Billboard", public=False,
                                        collaborative=False, description="")

sp.playlist_add_items(playlist_id=playlist_info["id"], items=song_uri_list, position=None)

