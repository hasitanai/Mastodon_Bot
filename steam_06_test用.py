from mastodon import *
from time import sleep
import threading, re, sys, io
import warnings, traceback
from xml.sax.saxutils import unescape as unesc
from xml.sax.saxutils import escape as esc

url_ins = open("instance.txt").read()

mastodon = Mastodon(
    client_id="cred.txt",
    access_token="auth.txt",
    api_base_url=url_ins)  # インスタンス

class Re1():
    def text(text):
        text = re.sub('<br />', '\n', str(text))
        text = re.sub('<p>|</p>|<a.+"tag">|<a.+"_blank">|<a.+mention">|<'
                      'span>|</span>|</a>|<span class="[a-z-]+">', "", text)
        return unesc(text, {"&apos;":"'", '&quot;':'"'})

class response_toot(StreamListener):
    def on_update(self, status):
        try:
            account = status["account"]
            content = status["content"]
            ct = account["statuses_count"]
            non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0x0000)
            print("===on_update===")
            print((account["display_name"]).translate(non_bmp_map) + "@" + str(
                account["acct"]).translate(non_bmp_map) + " [{}toot]".format(str(ct)))
            print(Re1.text(content).translate(non_bmp_map))
            print("---")
            # ここに受け取ったtootに対してどうするか追加してね（*'∀'人）
            pass
        except:
            print("エラー情報\n" + traceback.format_exc())
            pass

    def on_notification(self, notification):
        print("===on_notification===")
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0x0000)
        if notification["type"] == "favourite":
            account = notification["account"]
            print(str(account["display_name"]).translate(non_bmp_map) + "@" + str(
                account["acct"]) + "からニコってくれたよ₍₍ ◝(●˙꒳˙●)◜ ₎₎")
            print("---")
        elif notification["type"] == "reblog":
            account = notification["account"]
            print(str(account["display_name"]).translate(non_bmp_map) + "@" + str(
                account["acct"]) + "がブーストしてくれたよ(๑˃́ꇴ˂̀๑)")
            print("---")
        pass

    def on_delete(self, status_id):
        print("===on_delete===")
        print(status_id)
        pass

if __name__ == '__main__':
    listener = response_toot()
    #mastodon.local_stream(listener)
    mastodon.user_stream(listener)
