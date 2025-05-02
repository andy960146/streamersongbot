import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ★★★ 在這裡填你的資料 ★★★
CLIENT_ID = '你的spotify client ID'
CLIENT_SECRET = '你的spotify client secret'
REDIRECT_URI = 'http://127.0.0.1:8888/callback'

# 這是要求的權限範圍（需要可以搜尋、播放、控制音樂）
scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing streaming"

# 建立認證流程
sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope,
    cache_path=".cache"  # 存token的小檔案，避免每次都要重新認證
)

# 正式建立 Spotify物件
sp = spotipy.Spotify(auth_manager=sp_oauth)


