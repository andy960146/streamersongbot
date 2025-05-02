from twitch_bot import TwitchBot
from spotify_player import search_and_play, wait_for_song_end, get_dynamic_recommendation
from queue_server import update_queue_text, update_now_playing, skip_signal, song_queue, is_user_paused
from spotify_login import sp
import time

def on_new_song(song_name):
    song_queue.append(song_name)
    update_queue_text(song_queue)

def show_queue():
    update_queue_text(song_queue)

def send_chat_message(bot, message):
    try:
        bot.sock.send(f"PRIVMSG #{bot.channel} :{message}\r\n".encode("utf-8"))
    except Exception as e:
        print(f"⚠️ 傳送訊息失敗：{e}")

def run_main():
    bot = TwitchBot()
    bot.on_new_song(on_new_song)
    bot.queue_callback = show_queue
    bot.connect()
    bot.start()

    print("🚀 控制主程式啟動")
    
    play_mode = "queue"

    while True:
        if is_user_paused:
            print("⏸️ 使用者暫停中，主程式暫停播放流程...")
            time.sleep(3)
            continue

        playback = sp.current_playback()

        if play_mode == "queue":
            playback = sp.current_playback()
            if playback and playback.get("is_playing"):
                try:
                    sp.pause_playback()
                    time.sleep(2)
                except Exception as e:
                    print(f"⚠️ 清理播放失敗：{e}")

            try:
                sp.start_playback(uris=[])  # 🔥 清空目前播放佇列
                print("🧹 清空播放佇列")
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ 清空播放失敗：{e}")

            if song_queue:
                current_song = song_queue[0]
                print(f"🎶 開始播放歌曲：{current_song}")
                update_now_playing(current_song)
                send_chat_message(bot, f"🎵 現在播放：{current_song}")
                
                success = search_and_play(current_song)

                if not success:
                    print("⚠️ 播放失敗，跳過")
                    if song_queue:  # ✅ 加入保護
                        song_queue.pop(0)
                        update_queue_text(song_queue)
                    continue

                result = wait_for_song_end()

                if result in ["finished", "skipped"]:
                    if song_queue and song_queue[0] == current_song:  # ✅ 確保 current_song 仍存在再 pop
                        song_queue.pop(0)
                        update_queue_text(song_queue)
                    else:
                        print("⚠️ 播放完後歌單已被清空或變動，略過 pop")




            else:
                playback = sp.current_playback()
                if playback and (playback.get("is_playing") or is_user_paused):
                    print("⏸️ 排隊播放暫停中，等待...")
                    time.sleep(3)
                    continue
                print("⚠️ 排隊歌曲播放完畢，切換推薦模式")
                play_mode = "recommend"

        elif play_mode == "recommend":
            if song_queue:
                print("📥 偵測到新點歌，等推薦歌播完後切換 queue 模式")
                # 🔥 等推薦歌曲播放結束
                while True:
                    from queue_server import skip_signal
                    if skip_signal.is_set():
                        print("⏭️ 偵測到跳過指令，馬上切換 queue 模式")
                        skip_signal.clear()
                        break

                    playback = sp.current_playback()
                    if not playback or not playback.get("is_playing"):
                        break

                    time.sleep(2)

                play_mode = "queue"
                continue



            playback = sp.current_playback()
            if playback and playback.get("is_playing"):
                print("🎵 推薦歌曲正在播放，等待結束...")
                time.sleep(3)
                continue

            recommended = get_dynamic_recommendation()
            if recommended:
                send_chat_message(bot, f"🎧 正在播放推薦：{recommended}")
                for _ in range(10):
                    playback = sp.current_playback()
                    if playback and playback.get("is_playing"):
                        print("✅ 推薦歌曲播放確認成功")
                        break
                    print("⌛ 等待推薦歌曲開始播放...")
                    time.sleep(2)

                while True:
                    from queue_server import get_user_paused_status
                    if get_user_paused_status():
                        print("⏸️ 推薦歌曲暫停中，等待恢復...")
                        time.sleep(3)
                        continue
                    playback = sp.current_playback()
                    if not playback or not playback.get("is_playing"):
                        print("✅ 推薦歌曲播放結束")
                        break
                    time.sleep(3)
            else:
                print("⚠️ 推薦失敗，等待 10 秒重試")
                time.sleep(10)

if __name__ == "__main__":
    run_main()
