# -*- coding: utf-8 -*-

from mastodon import *
import time, re, sys, os, json, random
import threading, requests, pprint, codecs
from time import sleep
from datetime import datetime
from pytz import timezone
import warnings, traceback
import JCbot

warnings.simplefilter("ignore", UnicodeWarning)

"""ログイントークン取得済みで動かしてね（*'∀'人）"""

url_ins = open("instance.txt").read()

mastodon = Mastodon(
    client_id="cred.txt",
    access_token="auth.txt",
    api_base_url=url_ins)  # インスタンス

class Re1(): #Content整頓用関数
    def text(text):
        return (re.sub('<p>|</p>|<a.+"tag">|<a.+"_blank">|<a.+mention">|<span>|</span>|</a>|<span class="[a-z-]+">', "", str(text)))

class men_toot(StreamListener):
    def on_notification(self, notification):
        try:
            print("===通知が来ました===")
            non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
            if notification["type"] == "mention":
                status = notification["status"]
                account = status["account"]
                mentions = status["mentions"]
                content = Re1.text(status["content"])
                print("---")
                print(
                    str(account["display_name"]).translate(non_bmp_map) + "@" + str(account["acct"]).translate(
                        non_bmp_map))
                print(content.translate(non_bmp_map))
                print(str(mentions).translate(non_bmp_map))
                print("---")
                bot.n_sta = status
                bot.thank(account, 64)
                if mentions:
            elif notification["type"] == "favourite":
                account = notification["account"]
                print(str(account["display_name"]).translate(non_bmp_map) + "@" + str(
                    account["acct"]) + "からニコってくれたよ₍₍ ◝(●˙꒳˙●)◜ ₎₎")
                print()
                bot.thank(account, 32)
                print("---")
            pass
        except Exception as e:
            print("エラー情報\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
            pass


class res_toot(StreamListener):
    def on_update(self, status):
        try:
            print("===タイムライン===")
            account = status["account"]
            mentions = status["mentions"]
            content = status["content"]
            non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
            print((re.sub("<p>|</p>", "",
                          str(account["display_name"]).translate(non_bmp_map) + "@" + str(account["acct"]).translate(
                              non_bmp_map))))
            print((re.sub("<p>|</p>", "", str(content).translate(non_bmp_map))))
            print((re.sub("<p>|</p>", "", str(mentions).translate(non_bmp_map))))
            bot.check01(status)
            print("   ")
            #bot.block01(status)
            bot.res01(status)
            bot.res06(status)
            bot.res07(status)
            bot.fav01(status)
            bot.check00(status)
            bot.check02(status)
            # f = codecs.open('log\\' + 'log_' + '.txt', 'a', 'UTF-8')
            # f.write(str(status) + "\n")
            # f.close()
            pass
        except Exception as e:
            print("エラー情報\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
            pass

    def on_delete(self, status_id):
        print("===削除されました===")


class bot():
    def _init_(self):

class count():
    timer_toot = 0
    timer_hello = 0

    def emo01(time=10800):  # 定期的に評価を下げまーーす♪（無慈悲）
        while 1:
            sleep(time)
            data_dir_path = u"./thank/"
            file_list = os.listdir(r'./thank/')
            for file_name in file_list:
                root, ext = os.path.splitext(file_name)
                if ext == u'.txt':
                    abs_name = data_dir_path + '/' + file_name
                    f = open(abs_name, 'r')
                    x = f.read()
                    y = int(x)
                    y += -1
                    f.close()
                    f = open(abs_name, 'w')
                    f.write(str(y))
                    f.close()

    def emo02(point):
        sleep(time)
        data_dir_path = u"./thank/"
        file_list = os.listdir(r'./thank/')
        for file_name in file_list:
            root, ext = os.path.splitext(file_name)
            if ext == u'.txt':
                abs_name = data_dir_path + '/' + file_name
                f = open(abs_name, 'r')
                x = f.read()
                y = int(x)
                y += point
                f.close()
                f = open(abs_name, 'w')
                f.write(str(y))
                f.close()
        pass

    def emo03(user, point):
        sleep(time)
        data_dir_path = u"./thank/"
        file_list = os.listdir(r'./thank/')
        abs_name = data_dir_path + '/' + user + '.txt'
        f = open(abs_name, 'r')
        x = f.read()
        y = int(x)
        y += point
        f.close()
        f = open(abs_name, 'w')
        f.write(str(y))
        f.close()
        pass


def go():
    count.timer_hello = 1


if __name__ == '__main__':
    count()
    go()
    bot.timer_toot = False
    uuu = threading.Timer(0, bot.t_local)
    lll = threading.Timer(0, bot.t_user)
    uuu.start()
    lll.start()
    fff = threading.Timer(0, count.emo01, [10800])
    fff.start()
