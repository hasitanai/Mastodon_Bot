# -*- coding: utf-8 -*-

from mastodon import *
from time import sleep
import warnings
import re, sys, os, csv, json, codecs
import threading, requests, random
import requests
from datetime import datetime
from pytz import timezone
from xml.sax.saxutils import unescape as unesc
import traceback

warnings.simplefilter("ignore", UnicodeWarning)
url_ins = open("instance.txt").read()
mastodon = Mastodon(
    client_id="cred.txt",
    access_token="auth.txt",
    api_base_url=url_ins)  # インスタンス

jst_now = datetime.now(timezone('Asia/Tokyo'))
nowing = str(jst_now.strftime("%Y%m%d%H%M%S"))
with open('log\\' + 'log_' + nowing + '.txt', 'w') as f:
    f.write(str(jst_now))


class Re1():  # Content整頓用関数
    def text(text):
        return (re.sub('<p>|</p>|<a.+</a>|<span.+</span></a></span>', "", str(text)))


class res_toot(StreamListener):
    def on_update(self, status):
        try:
            account = status["account"]
            path = '\\thank\\' + account["acct"] + '.txt'
            if os.path.exists(path):
                f = open(os.path.abspath(os.path.dirname(__file__)) + path, 'r')
                x = f.read()
                f.close()
            else:
                x = 0
            if int(x) >= -10:
                mentions = Re1.text(status["mentions"])
                content = unesc(Re1.text(status["content"]))
                non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0x0000)
                """
                print((re.sub("<p>|</p>", "", str(account["display_name"]).translate(non_bmp_map)+ "@" + str(account["acct"]).translate(non_bmp_map)))) 
                print(content.translate(non_bmp_map))
                print(mentions.translate(non_bmp_map))
                print("   ")
                """
                del_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0x0000)
                text = (re.sub('\fffd|@.+ |https://.+($| )', '', str(content)))
                f = codecs.open('log\\' + 'log_' + nowing + '.txt', 'a', 'UTF-8')
                f.write(unesc(re.sub('<br />', '\\n', str(text)) + ',<acct="' + account["acct"] + '">\r\n'))
                f.close()
        except:
            print("エラー情報\n" + traceback.format_exc())
            with open('error_03.log', 'a') as f:
                traceback.print_exc(file=f)
            pass


class bot():
    def t_local():
        listener = res_toot()
        mastodon.local_stream(listener)


if __name__ == '__main__':
    l = threading.Timer(0, bot.t_local)
    l.start()
