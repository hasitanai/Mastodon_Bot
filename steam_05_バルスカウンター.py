# -*- coding: utf-8 -*-

from mastodon import *
from time import sleep
import warnings
import re
import sys
import codecs

warnings.simplefilter("ignore", UnicodeWarning)

"""ログイントークン取得済みで動かしてね（*'∀'人）"""
url_ins = open("instance.txt").read()

mastodon = Mastodon(
        client_id="cred.txt",
        access_token="auth.txt",
        api_base_url = url_ins) #インスタンス

class response_toot(StreamListener):
    def on_update(self, status):
        account = status["account"]
        content = status["content"]
        print("===on_update===")
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        print("---")
        print((re.sub("<p>|</p>", "", str(account["display_name"]).translate(non_bmp_map)+ "@" + str(account["acct"]).translate(non_bmp_map)))) 
        print((re.sub("<p>|</p>", "", str(content).translate(non_bmp_map))))
        if re.compile("バ(.*)ル(.*)ス|ﾊﾞ(.*)ﾙ(.*)ｽ|ば(.*)る(.*)す|BA(.?)RU(.?)SU").search(status['content']):
            print("◇Hit")
            count.bals += 1
            f = codecs.open('count\\bals.txt', 'w', 'utf-8')
            f.write(str(count.bals))
            f.close
        pass

    def on_notification(self, notification):
        print("===on_notification===")
        print(notification)
        pass

    def on_delete(self, status_id):
        print("===on_delete===")
        print(status_id)
        pass    

class count():
    f = codecs.open('count\\bals.txt', 'r', 'utf-8')
    bals = f.read()
    bals = int(bals)
    f.close
    

#def toot():
#    media_files = [mastodon.media_post(media, "image/jpeg") for media in ["test.jpg"]]
#    toot_now = input(u"toot: ")
#    mastodon.status_post(status=toot_now, media_ids=media_files, visibility=unlisted)
#    mastodon.status_post(status=toot_now, visibility="unlisted")
    """visibility   これで公開範囲を指定できるよ！: public, unlisted, private, direct"""

if __name__ == '__main__':
    count()
    listener = response_toot()
    mastodon.local_stream(listener)
    mastodon.user_stream(listener)
"""
「mastodon.」メソッドを下記の関数によって「ホーム」「連合」「ローカル」「指定のハッシュタグ」が選択できます
 user_stream, public_stream, local_stream, hashtag_stream(self, tag, listener, async=False)
"""
#    toot()　#上のStreamingAPIをサブスレッドで動かしながらこっちえお動かすか、別々で動かそうか迷うやつね。    


