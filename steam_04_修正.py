# -*- coding: utf-8 -*-

from mastodon import *
from time import sleep
import time
import warnings
import re
import sys
import threading
import requests
import pprint
import json
import codecs
import random
from datetime import datetime
import os
import traceback

warnings.simplefilter("ignore", UnicodeWarning)

"""ログイントークン取得済みで動かしてね（*'∀'人）"""

url_ins = open("instance.txt").read()

mastodon = Mastodon(
    client_id="cred.txt",
    access_token="auth.txt",
    api_base_url=url_ins)  # インスタンス


class men_toot(StreamListener):
    def on_notification(self, notification):
        print("===通知が来ました===")
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        if notification["type"] == "mention":
            status = notification["status"]
            account = status["account"]
            mentions = status["mentions"]
            content = status["content"]
            print("---")
            print(
                str(account["display_name"]).translate(non_bmp_map) + "@" + str(account["acct"]).translate(non_bmp_map))
            print((re.sub("<p>|</p>", "", str(content).translate(non_bmp_map))))
            print(str(mentions).translate(non_bmp_map))
            print("---")
            bot.n_sta = status
            bot.thank(account, 64)
            if mentions:
                if re.compile("おは|おあひょ").search(status['content']):
                    toot_now = "@" + str(account["acct"]) + " " + "（*'∀'人）おあひょーーーー♪"
                    g_vis = status["visibility"]
                    t = threading.Timer(8, bot.toot, [toot_now, g_vis, status['id']])
                    t.start()
                elif re.compile("こんに").search(status['content']):
                    toot_now = "@" + str(account["acct"]) + " " + "（*'∀'人）こんにちはーーーー♪"
                    g_vis = status["visibility"]
                    t = threading.Timer(8, bot.toot, [toot_now, g_vis, status['id']])
                    t.start()
                elif re.compile("こんば").search(status['content']):
                    toot_now = "@" + str(account["acct"]) + " " + "（*'∀'人）こんばんはーーーー♪"
                    g_vis = status["visibility"]
                    t = threading.Timer(8, bot.toot, [toot_now, g_vis, status['id']])
                    t.start()
                elif re.compile("\d+d(\d*)").search(status['content']):
                    inp = (re.sub("<span(.+)span>|<p>|</p>", "", str(status['content']).translate(non_bmp_map)))
                    result = bot.dice(inp)
                    g_vis = status["visibility"]
                    toot_now="@"+str(account["acct"])+"\n"+result
                    t = threading.Timer(5, bot.toot, [toot_now, g_vis, status['id']])
                    t.start()
            account = status["account"]
            v = threading.Timer(5, bot.fav_now)
            v.start()
        elif notification["type"] == "favourite":
            account = notification["account"]
            print(str(account["display_name"]).translate(non_bmp_map) + "@" + str(
                account["acct"]) + "からニコってくれたよ₍₍ ◝(●˙꒳˙●)◜ ₎₎")
            print()
            bot.thank(account, 32)
            print("---")
        pass


class res_toot(StreamListener):
    def on_update(self, status):
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
        bot.fav01(status)
        bot.res01(status)
        bot.res06(status)
        bot.res07(status)
        bot.check02(status)
        #f = codecs.open('log\\' + 'log_' + '.txt', 'a', 'UTF-8')
        #f.write(str(status) + "\n")
        #f.close()
        pass

    def on_delete(self, status_id):
        print("===削除されました===")


class bot():
    def _init_(self):
        self.g_sta = None
        self.n_sta = None

    def toot(toot_now, g_vis, rep=None):
        mastodon.status_post(status=toot_now, visibility=g_vis, in_reply_to_id=rep)
        """visibility   これで公開範囲を指定できるよ！: public, unlisted, private, direct"""

    def res07(status):
        if re.compile("ももな(.*)[1-5](\d*)").search(status['content']):
            print("○hitしました♪")
            non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
            coro = (re.sub("<p>|</p>", "", str(status['content']).translate(non_bmp_map)))
            toot_now = bot.dice(coro)
            g_vis = status["visibility"]
            t = threading.Timer(5, bot.toot, [toot_now, g_vis])
            t.start()
        elif re.compile("ももな(.*)([6-9]|\d{2})d(\d*)").search(status['content']):
            toot_now = "６回以上の回数は畳む内容だからメンションの方で送ってーー！！"
            g_vis = status["visibility"]
            t = threading.Timer(5, bot.toot, [toot_now, g_vis])
            t.start()

    def res01(status):
        account = status["account"]
        path = 'thank\\' + account["acct"] + '.txt'
        if os.path.exists(path):
            f = open(path, 'r')
            x = f.read()
            f.close()
        if int(x) >= -10:
            if account["acct"] != "JC":
                if count.timer_hello == 0:
                    if re.compile("ももな(.*)おは|ももな(.*)おあひょ").search(status['content']):
                        print("○hitしました♪")
                        print("○あいさつします（*'∀'人）")
                        toot_now = "(๑•̀ㅁ•́๑)✧おはありでーーーーす♪"
                        g_vis = "public"
                        t1 = threading.Timer(20, bot.toot, [toot_now, g_vis])
                        t1.start()
                        count.timer_hello = 1
                else:
                    if re.compile("[寝ね](ます|る|マス)(.*)[ぽお]や[すし]み|ももな(.*)[ぽお]や[すし]").search(status['content']):
                        if not re.compile("[寝ね]る(人|ひと)").search(status['content']):
                            print("○hitしました♪")
                            print("○おやすみします（*'∀'人）")
                            toot_now = account['display_name'] + "\n" + '(ृ 　 ु *`ω､)ु ⋆゜おやすみーーーー♪'
                            g_vis = "public"
                            t1 = threading.Timer(5, bot.toot, [toot_now, g_vis])
                            t1.start()        
                    elif re.compile("[いイ行逝]って(くる|きます|[きキ]マストドン)|出かけて|おでかけ|(出勤|離脱)し[てま]").search(status['content']):
                        print("○hitしました♪")
                        print("○見送ります（*'∀'人）")
                        toot_now = account['display_name'] + "\n" + 'いってらーーーー！！'
                        g_vis = "public"
                        t1 = threading.Timer(5, bot.toot, [toot_now, g_vis])
                        t1.start()
                    elif re.compile("ただいま|ただいマストドン").search(status['content']):
                        print("○hitしました♪")
                        print("○優しく迎えます（*'∀'人）")
                        toot_now = account['display_name'] + "\n" + '( 〃 ❛ᴗ❛ 〃 )おかえりおかえりーー！！'
                        g_vis = "public"
                        t1 = threading.Timer(5, bot.toot, [toot_now, g_vis])
                        t1.start()
                    else:   
                        try:
                            f = codecs.open('at_time\\' + account["acct"] + '.txt', 'r', 'UTF-8')
                            nstr = f.read()
                            f.close
                            print(nstr)
                            tstr = re.sub("\....Z", "", nstr)
                            last_time = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S')
                            nstr = status['created_at']
                            tstr = re.sub("\....Z", "", nstr)
                            now_time = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S')
                            delta = now_time - last_time
                            print(delta)
                            if delta.total_seconds() >= 10800:
                                if now_time.hour in range(3, 9):
                                    to_r = bot.rand_w('time\\kon.txt')
                                elif now_time.hour in range(9, 19):
                                    to_r = bot.rand_w('time\\kob.txt')
                                else:
                                    to_r = bot.rand_w('time\\oha.txt')
                                print("○あいさつします（*'∀'人）")
                                if account['display_name'] == "":
                                    toot_now = account['acct'] + "\n" + to_r
                                else:
                                    toot_now = account['display_name'] + "\n" + to_r
                                g_vis = "public"
                                t1 = threading.Timer(5, bot.toot, [toot_now, g_vis])
                                t1.start()
                        except:
                            print("○初あいさつします（*'∀'人）")
                            if account['statuses_count'] <= 2:
                                if account['display_name'] == "":
                                    toot_now = "@" + str(account["acct"]) + "\n" + account[
                                        'acct'] + "\n" + 'ようこそようこそーーーー♪'
                                else:
                                    toot_now = "@" + str(account["acct"]) + "\n" + account[
                                        'display_name'] + "\n" + 'ようこそようこそーーーー♪'
                            else:
                                if account['display_name'] == "":
                                    toot_now = account['acct'] + "\n" + 'いらっしゃーーーーい♪'
                                else:
                                    toot_now = account['display_name'] + "\n" + 'いらっしゃーーーーい♪'
                            g_vis = "public"
                            t1 = threading.Timer(5, bot.toot, [toot_now, g_vis])
                            t1.start()
        else:
            print("○反応がない人なので挨拶しません（*'∀'人）")

    def res06(status):
        account = status["account"]
        if account["acct"] != "JC":
            if re.compile("(.+)とマストドン(どちら|どっち)が大切か分かってない").search(status['content']):
                print("○hitしました♪")
                print("○だったら")
                toot_now = (re.sub("<p>|とマストドン(.*)", "", str(status['content']))) + "しながらマストドンして❤"
                g_vis = "public"
                t1 = threading.Timer(5, bot.toot, [toot_now, g_vis])
                t1.start()
                count.timer_hello = 1

    def fav01(status):
        if re.compile("ももな").search(status['content']):
            bot.n_sta = status
            account = status["account"]
            bot.thank(account, 8)
            v = threading.Timer(5, bot.fav_now)
            v.start()

    def check01(status):
        account = status["account"]
        created_at = status['created_at']
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        f = codecs.open('acct\\' + account["acct"] + '.txt', 'w', 'UTF-8')  # 書き込みモードで開く
        f.write(str(status["account"]).translate(non_bmp_map))  # アカウント情報の更新
        f.close()  # ファイルを閉じる
        path = 'thank\\' + account["acct"] + '.txt'
        if os.path.exists(path):
            f = open(path, 'r')
            x = f.read()
            print("現在の評価値:" + str(x))
            f.close()
        else:
            f = open(path, 'w')
            f.write("0")
            f.close()  # ファイルを閉じる

    def check02(status):
        account = status["account"]
        created_at = status['created_at']
        f = codecs.open('at_time\\' + account["acct"] + '.txt', 'w', 'UTF-8')  # 書き込みモードで開く
        f.write(str(status["created_at"]))  # \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z
        f.close()  # ファイルを閉じる

    def thank(account, point):
        path = 'thank\\' + account["acct"] + '.txt'
        if os.path.exists(path):
            f = open(path, 'r')
            x = f.read()
            y = int(x)
            y += point
            f.close()
            f = open(path, 'w')
            f.write(str(y))
            f.close()
            print("現在の評価値:" + str(y))
        else:
            f = open(path, 'w')
            f.write(str(point))
            f.close()  # ファイルを閉じる
            print("現在の評価値:" + str(0))

    def time_res():
        bot.timer_toot = 0
        print("「(๑•̀ㅁ•́๑)✧＜tootｽﾃﾝﾊﾞｰｲ」")

    def fav_now():  # ニコります
        fav = bot.n_sta["id"]
        mastodon.status_favourite(fav)
        print("◇Fav")

    def rand_w(txt_deta):
        f = codecs.open(txt_deta, 'r', 'utf-8')
        l = []
        for x in f:
            l.append(x.rstrip("\r\n").replace('\\n', '\n'))
        f.close()
        m = len(l)
        s = random.randint(1, m)
        return l[s - 1]

    def t_local():
        listener = res_toot()
        mastodon.local_stream(listener)

    def t_user():
        listener = men_toot()
        mastodon.user_stream(listener)

    def dice(inp):
        l=[]
        n=[]
        x=0
        try:
            r = re.search("\d+[dD]", str(inp))
            r = re.sub("[dD]", "", str(r.group()))
            if re.compile("(\d*):(\d*)").search(inp):
                s = re.sub("(.*)[dD](\d*):", "", str(inp))
                s = re.sub("[^\d]", "", str(s))
                print(str(s))
            m = re.search("[dD](\d*)", str(inp))
            m = re.sub("[dD]", "", str(m.group(1)))
            m = int(m)
            r = int(r)
            if m == 0:
                result = "面が0の数字は振れないよ……"
            elif r >= 51:
                result = "回数が長すぎるとめんどくさいから振らないよ……？"
            elif r == 0:
                result = "えっ……回数0？　じゃあ振らなーーーーい！"
            else:
                print(str(r)+"回"+str(m)+"面")
                print("○サイコロ振ります（*'∀'人）")
                for var in range(0, r):
                    num = random.randint(1, m)
                    num = str(num)
                    try:
                        if int(num) <= int(s):
                            result="ｺﾛｺﾛ……"+num+"成功だよーー！！"
                        else:
                            result="ｺﾛｺﾛ……"+num+"失敗だよ……"
                    except:
                        result="ｺﾛｺﾛ……"+num
                    l.append(result)
                    n.append(int(num))
                    x += int(num)
                if r != 1:
                    result=str(n)+" = "+str(x)
                    l.append(result)
                print(l)
                result = '\n'.join(l)
                if len(result) > 400:
                    result = "文字数制限に引っ掛かっちゃった……"
        except:
            traceback.print_exc()
            print("ちーん（昇天）")
            result="ごめんね、その数字だとサイコロ振れないの……"
        return result

class count():
    timer_toot = 0
    timer_hello = 0

    def emo01(time=0):  # 定期的に評価を下げまーーす♪（無慈悲）
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

def go():
    count.timer_hello = 1


if __name__ == '__main__':
    count()
    u = threading.Timer(0, bot.t_local)
    l = threading.Timer(0, bot.t_user)
    u.start()
    l.start()
    f = threading.Timer(0, count.emo01, [10800])
    f.start()
