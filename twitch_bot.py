import socket
import threading

NICKNAME = '你的Twitch帳號'
TOKEN = 'oauth:你的Twitch Token'  # ✅ 正確格式
CHANNEL = '你的Twitch帳號'

class TwitchBot:
    def __init__(self, nickname=NICKNAME, token=TOKEN, channel=CHANNEL):
        self.server = 'irc.chat.twitch.tv'
        self.port = 6667
        self.nickname = nickname
        self.token = token
        self.channel = channel
        self.sock = socket.socket()
        self.song_queue_callback = None

    def connect(self):
        self.sock.connect((self.server, self.port))
        self.sock.send(f"PASS {self.token}\r\n".encode('utf-8'))
        self.sock.send(f"NICK {self.nickname}\r\n".encode('utf-8'))
        self.sock.send(f"JOIN #{self.channel}\r\n".encode('utf-8'))
        print(f"✅ 已連接到Twitch頻道：#{self.channel}")

    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        while True:
            resp = self.sock.recv(2048).decode('utf-8')

            if resp.startswith('PING'):
                self.sock.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
                continue

            if 'PRIVMSG' in resp:
                username = resp.split('!', 1)[0][1:]
                message = resp.split('PRIVMSG', 1)[1].split(':', 1)[1].strip()
                print(f"[{username}] {message}")

                if message.startswith('!newsong '):
                    song_name = message[len('!newsong '):]
                    if self.song_queue_callback:
                        self.song_queue_callback(song_name)

                if message.strip() == '!queue':
                    if self.queue_callback:
                        self.queue_callback()


    def on_new_song(self, callback):
        self.song_queue_callback = callback
