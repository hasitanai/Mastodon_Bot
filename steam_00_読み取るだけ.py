# -*- coding: utf-8 -*-

from mastodon import *
from time import sleep
import threading, re, sys, io
import warnings, traceback

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,
                              encoding=sys.stdout.encoding,
                              errors='backslashreplace',
                              line_buffering=sys.stdout.line_buffering)
warnings.simplefilter("ignore", UnicodeWarning)

"""ログイントークン取得済みで動かしてね（*'∀'人）"""
url_ins = open("instance.txt").read()

mastodon = Mastodon(
    client_id="cred.txt",
    access_token="auth.txt",
    api_base_url=url_ins)  # インスタンス


# print(vars(mastodon))


class Re1():
    def text(text):
        return (re.sub('<p>|</p>|<a.+"tag">|<a.+"_blank">|<a.+mention">|<'
                       'span>|</span>|</a>|<span class="[a-z-]+">', "", str(text)))


class response_toot(StreamListener):
    def on_update(self, status):
        try:
            account = status["account"]
            content = status["content"]
            non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0x0000)
            print("===on_update===")
            print((account["display_name"]).translate(non_bmp_map) + "@" + str(
                account["acct"]).translate(non_bmp_map))
            print(Re1.text(content).translate(non_bmp_map))
            print("---")
            #        print(status)
            # ここに受け取ったtootに対してどうするか追加してね（*'∀'人）
            pass
        except:
            print("エラー情報\n" + traceback.format_exc())
            pass

    def on_notification(self, notification):
        print("===on_notification===")
        print(notification)
        pass

    def on_delete(self, status_id):
        print("===on_delete===")
        print(status_id)
        pass


def toot():
    #    media_files = [mastodon.media_post(media, "image/jpeg") for media in ["test.jpg"]]
    toot_now = input(u"toot: ")
    #    mastodon.status_post(status=toot_now, media_ids=media_files, visibility=unlisted)
    mastodon.status_post(status=toot_now, visibility="unlisted")
    """visibility   これで公開範囲を指定できるよ！: public, unlisted, private, direct"""


if __name__ == '__main__':
    listener = response_toot()
    mastodon.local_stream(listener)
# mastodon.user_stream(listener)
"""
「mastodon.」メソッドを下記の関数によって「ホーム」「連合」「ローカル」「指定のハッシュタグ」が選択できます
 user_stream, public_stream, local_stream, hashtag_stream(self, tag, listener, async=False)
"""
#    toot()　#上のStreamingAPIをサブスレッドで動かしながらこっちえお動かすか、別々で動かそうか迷うやつね。
