from mastodon import *
import time, re, sys, os, io
import threading, codecs
from time import sleep
import warnings, traceback
from xml.sax.saxutils import unescape as unesc
import JCbot as JC

#Winのプロンプトから起動用
"""
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,
                              encoding=sys.stdout.encoding,
                              errors='backslashreplace',
                              line_buffering=sys.stdout.line_buffering)
warnings.simplefilter("ignore", UnicodeWarning)
"""

"""ログイントークン取得済みで動かしてね（*'∀'人）"""

url_ins = open("instance.txt").read()

mastodon = Mastodon(
    client_id="cred.txt",
    access_token="auth.txt",
    api_base_url=url_ins)  # インスタンス

jst_now = datetime.now(timezone('Asia/Tokyo'))
nowing = str(jst_now.strftime("%Y%m%d%H%M%S"))
with open('log\\' + 'log_' + nowing + '.txt', 'w') as f:
    f.write(str(jst_now)+'\n')

class Re1():  # Content整頓用関数(๑°⌓°๑)
    def text(text):
        text = re.sub('<br />', '\n', str(text))
        return (re.sub('<p>|</p>|<a.+"tag">|<a.+"_blank">|<a.+mention">|<span>|'
                       '</span>|</a>|<span class="[a-z-]+">', "",
                       str(text)))
    

class Log():  # toot記録用クラス٩(๑❛ᴗ❛๑)۶
    def __init__(self, status):
        self.account = status["account"]
        self.mentions = status["mentions"]
        self.content = Re1.text(status["content"])
        self.content = unesc(self.content)
        self.non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

    def read(self):
        name = self.account["display_name"]
        acct = self.account["acct"]
        non_bmp_map = self.non_bmp_map
        print(str(name).translate(non_bmp_map) + "@" + str(
            acct).translate(self.non_bmp_map))
        print(str(self.content).translate(non_bmp_map))
        print(str(self.mentions).translate(non_bmp_map))

    def write(self):
        global nowing
        text = self.content
        acct = self.account["acct"]
        with codecs.open('log\\' + 'log_' + nowing + '.txt', 'a', 'UTF-8') as f:
            f.write(re.sub('<br />', '\\n', str(text)) + ',<acct="' + acct + '">\r\n')


class men_toot(StreamListener):  # 通知&ホーム監視クラス(๑・ .̫ ・๑)
    def on_notification(self, notification):
        try:
            print("===通知が来ました===", "タイプ:" + str(notification["type"]))
            if notification["type"] == "mention":
                status = notification["status"]
                account = status["account"]
                mentions = status["mentions"]
                content = unesc(Re1.text(status["content"]))
                log = threading.Thread(Log(status).read())
                log.run()
                men = threading.Thread(JC.MEN(status))
                men.run()
                bot.thank(account, 64)  # 好感度が上がります
            elif notification["type"] == "favourite":
                account = notification["account"]
                non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
                print(str(account["display_name"]).translate(non_bmp_map) + "@" + str(
                    account["acct"]) + "からニコってくれたよ₍₍ ◝(●˙꒳˙●)◜ ₎₎")
                bot.thank(account, 32)  # 好感度が上がります
            pass
        except Exception as e:
            print("エラー情報\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
            pass
        print("   ")

    def on_update(self, status):
        try:
            print("===タイムライン【ホーム】===")
            log = threading.Thread(Log(status).read())
            log.run()
            ltl = threading.Thread(JC.TL(status))
            ltl.run()
            pass
        except Exception as e:
            print("エラー情報\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
            pass
        print("   ")


class res_toot(StreamListener):  # LTL監視クラス((ヾ(๑ゝω･)ﾉ♡
    def on_update(self, status):
        try:
            print("===タイムライン【ローカル】===")
            log = threading.Thread(Log(status).read())
            log.run()
            ltl = threading.Thread(JC.LTL(status))
            ltl.run()
            pass
        except Exception as e:
            print("エラー情報\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
            pass
        print("   ")

    def on_delete(self, status_id):
        print("===削除されました===")
        print("   ")


class count():
    timer_toot = 0
    timer_hello = 0


class ready():
    def go():
        count.timer_hello = 1

    def stop():
        count.timer_hello = 0

if __name__ == '__main__':
    count()
    ready.go()
    bot.timer_toot = False
    uuu = threading.Thread(bot.t_local)
    lll = threading.Thread(bot.t_user)
    uuu.start()
    lll.start()
    
