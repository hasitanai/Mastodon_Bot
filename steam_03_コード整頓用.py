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

warnings.simplefilter("ignore", UnicodeWarning)

"""ログイントークン取得済みで動かしてね（*'∀'人）"""
url_ins = open("instance.txt").read()

mastodon = Mastodon(
        client_id="cred.txt",
        access_token="auth.txt",
        api_base_url = url_ins) #インスタンス


class men_toot(StreamListener):
    def on_notification(self, notification):
        global timer_hello
        print("●通知が来たよ！！")     
        if notification["type"] == "mention":
            status = notification["status"]
            account = status["account"]
            mentions = status["mentions"]
            content = status["content"] 
            non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
            print("---")
            print((re.sub("<p>|</p>", "", str(account["display_name"]).translate(non_bmp_map)+ "@" + str(account["acct"]).translate(non_bmp_map)))) 
            print((re.sub("<p>|</p>", "", str(content).translate(non_bmp_map))))
            print((re.sub("<p>|</p>", "", str(mentions).translate(non_bmp_map))))
            print("---")
            if mentions:
                if re.compile("おは|おあひょ").search(status['content']):
                    global toot_now
                    global g_vis
                    if account["acct"] == "lamazeP":
                        timer_hello = 1
                        print("test")
                        pass
                    toot_now = "@"+str(account["acct"])+" "+"（*'∀'人）おあひょーーーー♪"
                    g_vis = status["visibility"]
                    t = threading.Timer(8 ,toot)
                    t.start()
        pass
 
class res_toot(StreamListener):
    def on_update(self, status):
        global g_sta
        print("===タイムライン===")
        account = status["account"]
        mentions = status["mentions"]
        content = status["content"] 
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        print((re.sub("<p>|</p>", "", str(account["display_name"]).translate(non_bmp_map)+ "@" + str(account["acct"]).translate(non_bmp_map)))) 
        print((re.sub("<p>|</p>", "", str(content).translate(non_bmp_map))))
        print((re.sub("<p>|</p>", "", str(mentions).translate(non_bmp_map))))
        print("   ")
        g_sta = status
        check01()
        fav01()
        res01()
        res06()
        check02()
        pass

    def on_delete(self, status_id):
        print("===削除されました===")

    """
        global toot_now
        global g_vis
        toot_now = ":police_car: :police_car: :police_car:  ＜ｳ~ｳ~\nトゥー消し警察です！！！！\nToot番号「"+str(status_id)+"」を消した人ーー！！\n:gun: (๑•̀ㅁ•́๑)✧腹ばいになり手足を広げろーー！"
        g_vis = "unlisted"
        t = threading.Timer(8 ,toot)
        t.start()
        print(status_id)
        pass
    """

def toot(toot_now,g_vis):
    mastodon.status_post(status=toot_now, visibility=g_vis)
    """visibility   これで公開範囲を指定できるよ！: public, unlisted, private, direct"""

def res01():
        global timer_toot
        global g_sta
        global timer_hello
        status = g_sta
        account = status["account"]
        if account["acct"] != "JC":
            if timer_hello == 0:
                if re.compile("ももな(.*)おは|ももな(.*)おあひょ").search(status['content']):
                    print("○hitしました♪")
                    print("○あいさつします（*'∀'人）")
                    toot_now = "(๑•̀ㅁ•́๑)✧おはありでーーーーす♪"
                    g_vis = "public"
                    t1 = threading.Timer(20 ,toot,[toot_now,g_vis])
                    t1.start()
                    timer_hello = 1
            else:
                if re.compile("寝(ます|る|マス)(.*)[ぽお]や[すし]み|ももな(.*)[ぽお]や[すし]み").search(status['content']):
                    print("○hitしました♪")
                    print("○おやすみします（*'∀'人）")
                    toot_now = account['display_name']+"\n"+'(ृ 　 ु *`ω､)ु ⋆゜おやすみーーーー♪'
                    g_vis = "public"
                    t1 = threading.Timer(3 ,toot,[toot_now,g_vis])
                    t1.start() 
                else:
                    print("○hitしました♪")
                    try:
                        f = codecs.open('at_time\\'+account["acct"]+'.txt', 'r', 'UTF-8')
                        nstr = f.read()
                        f.close
                        print(nstr)
                        tstr = re.sub("\....Z","",nstr)
                        last_time = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S')
                        nstr = status['created_at']
                        tstr = re.sub("\....Z","",nstr)
                        now_time = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S')
                        delta = now_time - last_time
                        print(delta)
                        if delta.total_seconds() >= 10800:
                            if now_time.hour in range(3,9):
                                to_r = rand_w('time\\kon.txt')
                            elif now_time.hour in range(9,20):
                                to_r = rand_w('time\\kob.txt')
                            else:
                                to_r = rand_w('time\\oha.txt')
                            print("○あいさつします（*'∀'人）")
                            toot_now = account['display_name']+"\n"+to_r
                            #g_vis = "unlisted"
                            g_vis = "public"
                            t1 = threading.Timer(3 ,toot,[toot_now,g_vis])
                            t1.start()
                    except:    
                        print("○あいさつします（*'∀'人）")
                        toot_now = account['display_name']+"\n"+'いらっしゃい♪'
                        g_vis = "public"
                        t1 = threading.Timer(3 ,toot,[toot_now,g_vis])
                        t1.start() 

def res06():
        global timer_toot
        global g_sta
        status = g_sta
        account = status["account"]
        if account["acct"] != "JC":
            if re.compile("(.+)とマストドン(どちら|どっち)が大切か分かってない").search(status['content']):
                print("○hitしました♪")
                print("○だったら")
                toot_now = (re.sub("<p>|とマストドン(.*)", "", str(status['content'])))+"しながらマストドンして❤"
                g_vis = "public"
                t1 = threading.Timer(5 ,toot,[toot_now,g_vis])
                t1.start()
                timer_hello = 1


def fav01(): 
    global g_sta
    global n_sta
    status = g_sta
    if re.compile("ももな").search(status['content']):
        n_sta = status
        v = threading.Timer(1 ,fav_now)
        v.start()

def check01():
    global g_sta
    status = g_sta
    account = status["account"]
    created_at = status['created_at']
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    f = codecs.open('acct\\'+account["acct"]+'.txt', 'w', 'UTF-8') # 書き込みモードで開く
    f.write(str(status["account"]).translate(non_bmp_map)) # アカウント情報の更新
    f.close() # ファイルを閉じる

def check02():
    global g_sta
    status = g_sta
    account = status["account"]
    created_at = status['created_at']
    f = codecs.open('at_time\\'+account["acct"]+'.txt', 'w', 'UTF-8') # 書き込みモードで開く
    f.write(str(status["created_at"])) # \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z
    f.close() # ファイルを閉じる

def time_res():
    global timer_toot    
    timer_toot = 0
    print("「(๑•̀ㅁ•́๑)✧＜tootｽﾃﾝﾊﾞｰｲ」")

def fav_now(): #ニコります
    global n_sta
    fav = n_sta["id"]
    mastodon.status_favourite(fav)
    print("◇Fav")

def rand_w(txt_deta):
    f = codecs.open(txt_deta, 'r', 'utf-8')
    l = []
    for x in f:
        l.append(x.rstrip("\r\n").replace('\\n', '\n'))
    f.close()
    m = len(l)
    s = random.randint(1,m)
    return l[s-1]

def t_local():
    listener = res_toot()
    mastodon.local_stream(listener)

def t_user():
    listener = men_toot()
    mastodon.user_stream(listener)

if __name__ == '__main__':
    timer_toot = 0
    timer_hello = 1
    listener = res_toot()
    u = threading.Timer(0 ,t_local)
    l = threading.Timer(0 ,t_user)
    u.start()
    l.start()
#    toot()　#上のStreamingAPIをサブスレッドで動かしながらこっちえお動かすか、別々で動かそうか迷うやつね。    


