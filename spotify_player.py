import time
from spotify_login import sp
import random
from queue_server import update_now_playing

# ✅ 三個推薦播放清單 ID（中/日/英文）可以更換為自己想要的
playlist_ids = [
    "7MUBAm6nJvr8D3LuBTrYTC",  # 中文
    "3wnV76L140WU1nkAVCPNwn",  # 日文
    "4fkb8VqBPKsiVp4Zwzjl1U"   # 英文
]

def get_dynamic_recommendation():
    try:
        playlist_id = random.choice(playlist_ids)
        print(f"🎧 從推薦清單 {playlist_id} 撈取歌曲...")

        tracks = sp.playlist_tracks(playlist_id, limit=50, market='TW')
        items = tracks['items']
        if not items:
            print("⚠️ 無法從推薦清單取得歌曲")
            return None

        track = random.choice(items)['track']
        uri = track['uri']
        name = track['name']
        artist = track['artists'][0]['name']
        song_title = f"{name} - {artist}"
        print(f"🎧 抽到推薦歌曲：{song_title}")

        devices = sp.devices()
        device_id = None
        for d in devices['devices']:
            if d['is_active']:
                device_id = d['id']
                break

        if device_id:
            sp.start_playback(device_id=device_id, uris=[uri])
            update_now_playing(f"🎧 推薦：{song_title}")
            print(f"🎧 正在播放推薦：{song_title}")
            return song_title
        else:
            print("⚠️ 沒有找到播放裝置")
            return None

    except Exception as e:
        print(f"❌ 推薦播放失敗：{e}")
        return None

def play_recommendation():
    print("🎧 撥放推薦歌曲...")

    playlist_id = "37i9dQZF1DXcBWIGoYBM5M"  # 你可以換成自己的推薦清單

    tracks = sp.playlist_tracks(playlist_id, limit=50)
    items = tracks['items']

    if not items:
        print("⚠️ 推薦清單無法取得歌曲")
        return None

    track = random.choice(items)['track']
    uri = track['uri']
    name = track['name']
    artist = track['artists'][0]['name']
    song_title = f"{name} - {artist}"

    devices = sp.devices()
    device_id = None
    for d in devices['devices']:
        if d['is_active']:
            device_id = d['id']
            break

    if device_id:
        sp.start_playback(device_id=device_id, uris=[uri])
        print(f"🎧 正在播放推薦：{song_title}")
        update_now_playing(f"🎧 推薦：{song_title}")  # ✅ 同步給後台
        return song_title
    else:
        print("⚠️ 沒有播放裝置")
        return None

from queue_server import get_user_paused_status, skip_signal

def wait_for_song_end():
    waiting_for_start = True

    while True:
        playback = sp.current_playback()

        if not playback:
            time.sleep(2)
            continue

        if get_user_paused_status():
            print("⏸️ 使用者暫停播放中，等待恢復...")
            time.sleep(2)
            continue

        if skip_signal.is_set():
            print("⏭️ 偵測到跳過指令，切到下一首歌")
            skip_signal.clear()
            try:
                sp.next_track()
            except Exception as e:
                print(f"⚠️ 跳下一首失敗：{e}")
            return "skipped"

        if waiting_for_start:
            item = playback.get("item")
            if playback.get("is_playing") and item and item.get("id"):
                print(f"✅ 歌曲 {item.get('name', '(無名)')} 開始播放")
                waiting_for_start = False
            else:
                time.sleep(1)
                continue
        else:
            if not playback.get("is_playing"):
                print("✅ 歌曲自然播放完畢")
                return "finished"

        time.sleep(2)






def search_and_play(song_name):
    print(f"🔎 搜尋歌曲：{song_name}")
    result = sp.search(q=song_name, limit=1, type='track')

    # ✅ 檢查是否有找到歌曲
    if not result['tracks']['items']:
        print(f"⚠️ 找不到這首歌：{song_name}")
        return False  # ❗播放失敗

    track = result['tracks']['items'][0]
    uri = track['uri']
    print(f"🎵 播放：{track['name']} - {track['artists'][0]['name']}")

    devices = sp.devices()
    device_id = None
    for d in devices['devices']:
        if d['is_active']:
            device_id = d['id']
            break

    if device_id:
        sp.start_playback(device_id=device_id, uris=[uri])
        return True  # ✅ 播放成功
    else:
        print("⚠️ 找不到播放裝置，請開啟 Spotify App！")
        return False
