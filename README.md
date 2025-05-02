# streamersongbot
這是一款專為 Twitch 直播主打造的 Spotify 點歌機器人，結合 Twitch 聊天室互動與 Spotify 播放功能，讓觀眾能即時點播歌曲，直播主也能輕鬆管理歌單。它同時內建推薦播放功能，在沒有點歌時自動播放隨機歌單，保持直播氣氛不冷場。
<details> 
<summary>🚀 <strong>完整安裝指南（點此展開）</strong></summary>

```
bash
# 1️⃣ 安裝 Python 3.8+
python --version

# 2️⃣ 安裝 pip（如已內建可略過）

# 3️⃣ 下載專案
git clone https://github.com/YOUR_USERNAME/streamersongbot.git
cd streamersongbot

# 4️⃣ 安裝必要套件
pip install -r requirements.txt
```
---
🔧 Twitch 機器人設定

打開 `twitch_bot.py` 修改以下內容：
```
python
NICKNAME = '你的Twitch帳號'
TOKEN = 'oauth:你的Twitch OAuth Token'
CHANNEL = '你的Twitch頻道名稱'
```
Twitch Token 取得方式：

到 [Twitch Token Generator](https://twitchtokengenerator.com/) 取得 `chat:read` + `chat:edit` 權限的 Token。

---
🔧 Spotify 機器人設定

打開 `spotify_login.py` 修改以下內容：
```
python
CLIENT_ID = '你的Spotify Client ID'
CLIENT_SECRET = '你的Spotify Client Secret'
REDIRECT_URI = 'http://127.0.0.1:8888/callback'
```
Spotify Key 取得方式：

1️⃣ 到 [Spotify 開發者中心](https://developer.spotify.com/dashboard)。

2️⃣ 創建應用，取得 Client ID 和 Client Secret。

3️⃣ 在 Redirect URI 加入：`http://127.0.0.1:8888/callback`。

---
🔧 Ngrok 路徑設定

打開 `start_server.py` 修改：
```
python
ngrok_path = r"C:\路徑\到你的\ngrok.exe"
```
💡 建議改寫成同資料夾執行：
```
python
import os
ngrok_path = os.path.join(os.path.dirname(__file__), "ngrok.exe")
```
---
🚀 啟動機器人
```
bash
python start_server.py
```
✅ 啟動後會自動開啟：

‧控制台：`http://127.0.0.1:8888/admin`

‧Ngrok 外網網址(可以讓nightbot抓資料)
---
💡 聊天指令

| 指令               | 功能                     |
|--------------------|--------------------------|
| `!newsong 歌名`    | 新增歌曲到排隊清單       |
| `!queue`           | 顯示目前排隊歌單         |

---
Night Bot設定(可做可不做)

功能<聊天室抓排隊歌單>

設定Commands:
```
Name:自訂指令
Response:$(urlfetch ngrok外部網址/)
Required User-Level:Everyone
```
</details>


