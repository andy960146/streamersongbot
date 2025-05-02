from flask import Flask, Response, render_template_string, redirect, jsonify, request
import threading

app = Flask(__name__)

# 全域變數
song_queue = []
queue_text = "⚠️ 目前沒有排隊中的歌曲！"
now_playing = ""
skip_signal = threading.Event()
is_user_paused = False

def get_user_paused_status():
    global is_user_paused
    return is_user_paused

# ✅ 給 main_core 用的更新函式
def update_queue_text(new_queue):
    global song_queue, queue_text
    song_queue = new_queue
    if song_queue:
        display_count = 5
        display_list = song_queue[:display_count]
        message = ' ｜ '.join(f"{idx+1}. {song}" for idx, song in enumerate(display_list))
        if len(song_queue) > display_count:
            message += f" ｜ ...還有 {len(song_queue) - display_count} 首等待播放"
        queue_text = message
    else:
        queue_text = "⚠️ 目前沒有排隊中的歌曲！"

def update_now_playing(song_name):
    global now_playing
    now_playing = song_name

# ✅ 給 Nightbot 用的 queue 清單文字
@app.route('/')
def get_queue():
    return Response(queue_text, mimetype='text/plain; charset=utf-8')

# ✅ 控制台主頁（AJAX版）
@app.route('/admin')
def admin():
    return render_template_string(f"""
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>🎛️ Twitch 控制台</title>
    <style>
        body {{ font-family: sans-serif; text-align: center; padding: 30px; }}
        h1 {{ margin-bottom: 10px; }}
        #now, #queue {{ margin: 10px 0; font-size: 20px; }}
    </style>
    <script>
        function updateStatus() {{
            fetch('/status').then(r => r.text()).then(txt => {{
                document.getElementById('now').innerText = txt;
            }});
            fetch('/queue').then(r => r.text()).then(txt => {{
                document.getElementById('queue').innerHTML = txt;
            }});
        }}
        setInterval(updateStatus, 5000);  // 每5秒更新
        window.onload = updateStatus;
    </script>
</head>
<body>
    <h1>🎛️ Twitch 點歌控制台</h1>
    <h2 id="now">🎵 正在讀取...</h2>
    <hr>
    <h3>📋 排隊清單（最多顯示5首）</h3>
    <p id="queue">讀取中...</p>
    <hr>
    <form action="/clear_queue" method="post">
        <button style="font-size: 22px; padding: 10px 30px;">🗑️ 清空歌單</button>
    </form>
    <form action="/skip_song" method="post">
        <button style="font-size: 22px; padding: 10px 30px;">⏭️ 跳過目前歌曲</button>
    </form>
    <form action="/pause_song" method="post">
        <button style="font-size: 22px; padding: 10px 30px; margin: 10px;">⏸️ 暫停播放</button>
    </form>
    <form action="/resume_song" method="post">
        <button style="font-size: 22px; padding: 10px 30px; margin: 10px;">▶️ 繼續播放</button>
    </form>
                                                                
</body>
</html>
""")

# ✅ 給 AJAX 抓目前正在播放
@app.route("/status")
def status():
    try:
        from spotify_login import sp
        playback = sp.current_playback()
        if playback and playback.get("item"):
            name = playback["item"]["name"]
            artist = playback["item"]["artists"][0]["name"]
            is_playing = playback["is_playing"]

            if is_playing:
                status = f"🎧 正在播放：{name} - {artist}"
            else:
                status = f"⏸️ 已暫停播放：{name} - {artist}（稍後將繼續）"
        else:
            status = "⚠️ Spotify 播放狀態無法取得"
    except Exception as e:
        status = f"❌ 錯誤：{e}"
    return status


# ✅ 給 AJAX 抓目前排隊歌單
@app.route('/queue')
def get_queue_ajax():
    if not song_queue:
        return "⚠️ 無歌曲排隊"
    lines = [f"{idx+1}. {song}" for idx, song in enumerate(song_queue[:5])]
    if len(song_queue) > 5:
        lines.append(f"...還有 {len(song_queue)-5} 首等待播放")
    return "<br>".join(lines)

# ✅ 清空歌單
@app.route('/clear_queue', methods=['POST'])
def clear_queue():
    global song_queue, queue_text, now_playing
    song_queue.clear()
    queue_text = "⚠️ 目前沒有排隊中的歌曲！"
    now_playing = ""
    return redirect("/admin")

# ✅ 跳過目前歌曲
@app.route('/skip_song', methods=['POST'])
def skip_song():
    skip_signal.set()
    return redirect("/admin")

def run_flask():
    app.run(host="0.0.0.0", port=8888)

@app.route('/pause_song', methods=['POST'])
def pause_song():
    global is_user_paused
    try:
        from spotify_login import sp
        sp.pause_playback()
        is_user_paused = True  # ✅ 標記為手動暫停
        print("⏸️ 已暫停播放")
    except Exception as e:
        print(f"⚠️ 暫停播放失敗：{e}")
    return redirect("/admin")


@app.route('/resume_song', methods=['POST'])
def resume_song():
    global is_user_paused
    try:
        from spotify_login import sp
        sp.start_playback()
        is_user_paused = False  # ✅ 解除暫停標記
        print("▶️ 已恢復播放")
    except Exception as e:
        print(f"⚠️ 恢復播放失敗：{e}")
    return redirect("/admin")

