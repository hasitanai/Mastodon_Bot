# -*- coding: utf-8 -*-

from mastodon import *
import time, re, sys, os, json, random
import threading, requests, pprint, codecs
from time import sleep
from datetime import datetime
from pytz import timezone
import warnings, traceback

warnings.simplefilter("ignore", UnicodeWarning)

"""ログイントークン取得済みで動かしてね（*'∀'人）"""

url_ins = open("instance.txt").read()

mastodon = Mastodon(
    client_id="cred.txt",
    access_token="auth.txt",
    api_base_url=url_ins)  # インスタンス


class Re1():  # Content整頓用関数
    def text(text):
        return (re.sub('<p>|</p>|<a.+"tag">|<a.+"_blank">|<a.+mention">|<span>|</span>|</a>|<span class="[a-z-]+">', "",
                       str(text)))

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
                    if re.compile("おは|おあひょ").search(content):
                        toot_now = "@" + str(account["acct"]) + " " + "（*'∀'人）おあひょーーーー♪"
                        g_vis = status["visibility"]
                        bot.rets(8, toot_now, g_vis, status['id'])
                    elif re.compile("こんに").search(content):
                        toot_now = "@" + str(account["acct"]) + " " + "（*'∀'人）こんにちはーーーー♪"
                        g_vis = status["visibility"]
                        bot.rets(8, toot_now, g_vis, status['id'])
                    elif re.compile("こんば").search(content):
                        toot_now = "@" + str(account["acct"]) + " " + "（*'∀'人）こんばんはーーーー♪"
                        g_vis = status["visibility"]
                        bot.rets(8, toot_now, g_vis, status['id'])
                    elif re.compile("\d+[dD]\d+").search(content):
                        inp = (re.sub("<span class(.+)</span></a></span>|<p>|</p>", "",
                                      str(status['content']).translate(non_bmp_map)))
                        result = game.dice(inp)
                        g_vis = status["visibility"]
                        toot_now = ":@" + str(account["acct"]) + ": @" + account["acct"] + "\n" + result
                        bot.rets(5, toot_now, g_vis, status['id'])
                    elif re.compile("アラーム(\d+)").search(content):
                        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
                        content = str(status['content']).translate(non_bmp_map)
                        account = status['account']
                        com = re.search("(アラーム|[Aa][Rr][Aa][Mm])(\d+)([秒分]?)", content)
                        sec = int(com.group(2))
                        clo = com.group(3)
                        if clo == "分":
                            sec = sec * 60
                        else:
                            pass
                        print(str(sec))
                        toot_now = "@" + account["acct"] + " " + "（*'∀'人）時間だよーー♪♪"
                        g_vis = status["visibility"]
                        in_reply_to_id = status["id"]
                        bot.rets(int(com.group(1)),toot_now, g_vis, status['id'])
                    elif re.compile(
                            "(フォロー|follow)(して|く[うぅー]*ださ[あぁー]*い|お願[あぁー]*い|おねが[あぁー]*い|頼[むみ]|たの[むみ]|ぷりーず|プリーズ|please)").search(
                            content):
                        mastodon.account_follow(account["id"])
                        toot_now = "@" + account["acct"] + " " + "（*'∀'人）フォローしました♪♪"
                        g_vis = status["visibility"]
                        in_reply_to_id = status["id"]
                        bot.rets(8, toot_now, g_vis, status['id'])
                    elif re.compile("(こそこそ)<br />(.+)").search(content):  # 悪用されないように変えてます
                        if status["visibility"] == "direct":
                            print("○受け取りました")
                            com = re.search("(こそこそ).*<br />(.+)", str(content))
                            messe = com.group(2)
                            toot_now = messe
                            g_vis = "public"
                            bot.rets(1, toot_now, g_vis)
                    elif re.compile("連想ゲーム開始").search(content):
                        if rensou_time:
                            toot_now = "@" + account["acct"] + " " + "（*'∀'人）ごめんね、今開催中なの♪♪"
                            g_vis = status["visibility"]
                            in_reply_to_id = status["id"]
                            bot.rets(5, toot_now, g_vis, status['id'])
                        else:
                            t = threading.Timer(0, game.rensou)
                            t.start()
                            rensou_time = True
                    else:
                        pass
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
            # bot.block01(status)
            bot.res01(status)
            bot.res06(status)
            bot.res07(status)
            bot.fav01(status)
            bot.check00(status)
            bot.check02(status)
            game.poem(status)
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
        self.g_sta = None
        self.n_sta = None

    def rets(sec, toot_now, g_vis, rep=None):
        t = threading.Timer(sec, bot.toot, [toot_now, g_vis, rep])
        t.start()

    def toot(toot_now, g_vis, rep=None):
        mastodon.status_post(status=toot_now, visibility=g_vis, in_reply_to_id=rep)
        """visibility   これで公開範囲を指定できるよ！: public, unlisted, private, direct"""

    def block01(status):
        f = codecs.open("NG\sekuhara.txt", 'r', 'utf-8')
        l = []
        for x in f:
            l.append(x.rstrip("\r\n"))
        f.close()
        m = len(l)
        for x in range(m):
            if re.compile(str(l[x])).search(re.sub("<p>|</p>", "", str(status))):
                j = True
                break
            else:
                j = False
        return j

    def res07(status):
        account = status["account"]
        if account['acct'] != "kiri_bot01":
            if not bot.timer_toot:
                if re.compile("ももな(.*)[1-5][dD]\d+").search(status['content']):
                    print("○hitしました♪")
                    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
                    coro = (re.sub("<p>|</p>", "", str(status['content']).translate(non_bmp_map)))
                    toot_now = ":@" + account["acct"] + ": @" + account["acct"] + "\n" + game.dice(coro)
                    g_vis = status["visibility"]
                    bot.rets(5, toot_now, g_vis)
                    w = threading.Timer(30, bot.time_res)
                    w.start()
                    bot.timer_toot = True
                elif re.compile("ももな(.*)([6-9]|\d{2})[dD](\d*)").search(status['content']):
                    toot_now = "６回以上の回数は畳む内容だからメンションの方で送ってーー！！"
                    g_vis = status["visibility"]
                    bot.rets(5, toot_now, g_vis)
                    w = threading.Timer(60, bot.time_res)
                    w.start()
                    bot.timer_toot = True

    def check00(status):
        account = status["account"]
        ct = account["statuses_count"]
        path = 'thank\\' + account["acct"] + '.txt'
        if os.path.exists(path):
            f = open(path, 'r')
            x = f.read()
            f.close()
        if int(x) >= -10:
            if account["acct"] == "JC":
                ct += 1
                if re.match('^\d+000$', str(ct)):
                    toot_now = "°˖✧◝(⁰▿⁰)◜✧˖" + str(ct) + 'toot達成ーーーー♪♪'
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)
            else:
                if re.match('^\d+0000$', str(ct)):
                    toot_now = " :@" + account['acct'] + ": @" + account['acct'] + "\n°˖✧◝(⁰▿⁰)◜✧˖" + str(
                        ct) + 'tootおめでとーーーー♪♪'
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)
                elif re.match('^\d000$', str(ct)):
                    toot_now = " :@" + account['acct'] + ": @" + account['acct'] + "\n（*'∀'人）" + str(ct) + 'tootおめでとーー♪'
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)
            if account["acct"] == "lamazeP":  # ラマーズＰ監視隊
                ct += 5
                if re.match('^\d+000$', str(ct)):
                    toot_now = "@lamazeP (๑•̀ㅁ•́๑)" + str(ct) + 'tootまであと5だよ！！！！'
                    g_vis = "direct"
                    bot.rets(5, toot_now, g_vis)
        else:
            pass

    def res01(status):
        account = status["account"]
        content = re.sub("<p>|</p>", "", str(status['content']))
        path = 'thank\\' + account["acct"] + '.txt'
        if os.path.exists(path):
            f = open(path, 'r')
            x = f.read()
            f.close()
        if int(x) >= -10:
            if account["acct"] != "JC":
                if count.timer_hello == 0:
                    if re.compile("ももな(.*)おは|ももな(.*)おあひょ").search(content):
                        print("○hitしました♪")
                        print("○あいさつします（*'∀'人）")
                        toot_now = "(๑•̀ㅁ•́๑)✧おはありでーーーーす♪"
                        g_vis = "public"
                        bot.rets(20, toot_now, g_vis)
                        count.timer_hello = 1
                else:
                    if re.compile("[寝ね](ます|る|マス)(.*)[ぽお]や[すし]|ももな(.*)[ぽお]や[すし]").search(content):
                        if not re.compile("[寝ね]る(人|ひと)").search(status['content']):
                            print("○hitしました♪")
                            print("○おやすみします（*'∀'人）")
                            if account['acct'] == "5":  # やなちゃん専用挨拶
                                print("○やなちゃんだ！！（*'∀'人）")
                                toot_now = ":@" + account[
                                    'acct'] + ":" + "やなちゃん！！！！！！" + "\n" + '(｡>﹏<｡)あとで一緒に寝るーーーー！！！！'
                            else:
                                toot_now = ":@" + account['acct'] + ":" + account[
                                    'display_name'] + "\n" + '(ृ 　 ु *`ω､)ु ⋆゜おやすみーーーー♪'
                            g_vis = "public"
                            bot.rets(5, toot_now, g_vis)
                    elif re.compile(
                            "[いイ行逝]って(くる|きます|[きキ]マストドン)|出かけて(くる|きま[あぁー]*す|[きキ]マストドン)|おでかけ(する|しま[あぁー]*す|[しシ]マストドン)|(出勤|離脱|しゅっきん|りだつ)(する|しま[あぁー]*す|[しシ]マストドン)|^(出勤|離脱)$|(.+)して(くる|きま[あぁー]*す|[きキ]マストドン)([ー～！。よぞね]|$)").search(
                        content):
                        print("○hitしました♪")
                        print("○見送ります（*'∀'人）")
                        if account['acct'] == "5":  # やなちゃん専用挨拶
                            print("○やなちゃんだ！！（*'∀'人）")
                            toot_now = ":@" + account['acct'] + ":" + "やなちゃん！！！！！！" + "\n" + '(*>_<*)ﾉいってらいってらーーーー！！！！'
                        else:
                            toot_now = ":@" + account['acct'] + ":" + account['display_name'] + "\n" + 'いってらーーーー！！'
                        g_vis = "public"
                        bot.rets(5, toot_now, g_vis)
                    elif re.compile("ただいま|ただいマストドン").search(content):
                        print("○hitしました♪")
                        print("○優しく迎えます（*'∀'人）")
                        if account['acct'] == "5":  # やなちゃん専用挨拶
                            print("○やなちゃんだ！！（*'∀'人）")
                            toot_now = ":@" + account['acct'] + ":" + "やなちゃん！！！！！！" + "\n" + '٩(๑❛ᴗ❛๑)۶おかえりおかえりーー！！'
                        else:
                            toot_now = ":@" + account['acct'] + ":" + account[
                                'display_name'] + "\n" + '( 〃 ❛ᴗ❛ 〃 )おかえりおかえりーー！！'
                        g_vis = "public"
                        bot.rets(5, toot_now, g_vis)
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
                            if delta.total_seconds() >= 604800:
                                if account['acct'] == "5":  # やなちゃん専用挨拶
                                    print("○やなちゃんだ！！（*'∀'人）")
                                    toot_now = ":@" + account['acct'] + ":" + "やなちゃん！！！！！！" + "\n" + "（*'∀'人）おひさひさーーーー♪"
                                else:
                                    toot_now = " :@" + account['acct'] + ":\n" + account[
                                        'acct'] + "\n" + "（*'∀'人）おひさひさーーーー♪"
                                g_vis = "public"
                                bot.rets(5, toot_now, g_vis)
                            elif delta.total_seconds() >= 10800:
                                if now_time.hour in range(3, 9):
                                    to_r = bot.rand_w('time\\kon.txt')
                                elif now_time.hour in range(9, 19):
                                    to_r = bot.rand_w('time\\kob.txt')
                                else:
                                    to_r = bot.rand_w('time\\oha.txt')
                                if account['acct'] == "5":  # やなちゃん専用挨拶
                                    print("○やなちゃんだ！！（*'∀'人）")
                                    toot_now = ":@" + account['acct'] + ":" + "やなちゃん！！！！！！" + "\n" + to_r
                                else:
                                    print("○あいさつします（*'∀'人）")
                                    if account['display_name'] == "":
                                        toot_now = ":@" + account['acct'] + ":" + account['acct'] + "\n" + to_r
                                    else:
                                        toot_now = ":@" + account['acct'] + ":" + account['display_name'] + "\n" + to_r
                                g_vis = "public"
                                bot.rets(5, toot_now, g_vis)
                        except:
                            print("○初あいさつします（*'∀'人）")
                            if account['statuses_count'] <= 2:
                                if account['display_name'] == "":
                                    toot_now = " :@" + account['acct'] + ": @" + account['acct'] + "\n" + account[
                                        'acct'] + "\n" + 'ようこそようこそーーーー♪'
                                else:
                                    toot_now = " :@" + account['acct'] + ": @" + account['acct'] + "\n" + account[
                                        'display_name'] + "\n" + 'ようこそようこそーーーー♪'
                            else:
                                if account['display_name'] == "":
                                    toot_now = " :@" + account['acct'] + ": @" + account['acct'] + "\n" + 'いらっしゃーーーーい♪'
                                else:
                                    toot_now = " :@" + account['acct'] + ": @" + account['acct'] + "\n" + 'いらっしゃーーーーい♪'
                            g_vis = "public"
                            bot.rets(5, toot_now, g_vis)
        else:
            print("○反応がない人なので挨拶しません（*'∀'人）")

    def res06(status):
        account = status["account"]
        content = Re1.text(status["content"])
        if account["acct"] != "JC":
            if re.compile("(.+)とマストドン(どちら|どっち)が大[切事]か[分わ]かってない").search(content):
                print("○hitしました♪")
                sekuhara = bot.block01(status)
                if len(content) > 60:
                    toot_now = "٩(๑`^´๑)۶長い！！！！！！"
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)
                else:
                    if not sekuhara:
                        print("○だったら")
                        toot_now = ":@" + account["acct"] + ":" + (
                        re.sub('<span(.+)span>|<p>|とマストドン(.*)', "", str(content))) + "しながらマストドンして❤"
                        g_vis = "public"
                        bot.rets(5, toot_now, g_vis)
                    else:
                        toot_now = "そんなセクハラ分かりません\n(* ,,Ծ‸Ծ,, )ﾌﾟｰ"
                        g_vis = "public"
                        bot.rets(5, toot_now, g_vis)
                bot.timer_toot = 1
                t3 = threading.Timer(60, bot.time_res)
                t3.start()

    def fav01(status):
        account = status["account"]
        if re.compile("ももな|:@JC:").search(status['content']):
            bot.n_sta = status
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
        bot.timer_toot = False
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
        try:
            listener = res_toot()
            mastodon.local_stream(listener)
        except:
            print("例外情報\n" + traceback.format_exc())
            with open('except.log', 'a') as f:
                jst_now = datetime.now(timezone('Asia/Tokyo'))
                f.write("【" + str(jst_now) + "】")
                traceback.print_exc(file=f)
            sleep(180)
            bot.t_local()
            pass

    def t_user():
        try:
            listener = men_toot()
            mastodon.user_stream(listener)
        except:
            print("例外情報\n" + traceback.format_exc())
            with open('except.log', 'a') as f:
                jst_now = datetime.now(timezone('Asia/Tokyo'))
                f.write("【" + str(jst_now) + "】")
                traceback.print_exc(file=f)
            sleep(180)
            bot.t_user()
            pass


class game():
    rensou_time = False

    def fav(id):
        mastodon.status_favourite(id)
    
    def rensou(status):
        """

        toot = bot.toot
        toot("٩(๑❛ᴗ❛๑)۶今から連想ゲームを始めます！！", "")

        
        
　　　　"""
        pass

    def poem(status):
        account = status["account"]
        content = Re1.text(status["content"])
        if re.compile("(ぽえむ|ポエム)(ゲーム|げーむ)[：:]").search(content):
            poes = re.search("(ぽえむ|ポエム)(ゲーム|げーむ)[：:]<br />(.*)", str(content))
            Poe = poes.group(3)
            if len(content) > 60:
                    toot_now = "٩(๑`^´๑)۶長い！！！！！！"
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)
            else:
                Poe = re.sub("<br />", "\\n", Poe) 
                f = codecs.open('game\\poem_word.txt', 'a', 'UTF-8')
                f.write(str(Poe) + "," + account["acct"] + "\r\n" )
                f.close()
                v = threading.Timer(5, game.fav, [status["id"]])
                v.start()
        elif re.compile("ももな.*(ぽえむ|ポエム)(ゲーム|げーむ).*(ひとつ|おねがい)").search(content):
            f = codecs.open('game\\poem_word.txt', 'r', 'utf-8')
            word1 = []
            for x in f:
                word1.append(x.rstrip("\r\n").replace('\\n', '\n'))
            f.close()
            m = len(word1)
            word2 = []
            for x in range(4):
                s = random.randint(0, m-1)
                word2.append((word1[s]).split(','))
            poe0 = word2[0]
            poe1 = word2[1]
            poe2 = word2[2]
            poe3 = word2[3]
            toot_now = poe0[0] + "(by:@" + poe0[1] + ":)\n" + poe1[
                0] + "(by:@" + poe1[1] + ":)\n" + poe2[0] + "(by:@" + poe2[
                    1] + ":)\n" + poe3[0] + "(by:@" + poe3[1] + ":)\n#ぽえむげーむ"
            g_vis = "public"
            bot.rets(8, toot_now, g_vis)
        pass
    
    def dice(inp):
        l = []
        n = []
        m = []
        x = 0
        try:
            inp = re.sub("&lt;", "<", str(inp))
            inp = re.sub("&gt;", ">", str(inp))
            com = re.search("(\d+)[dD](\d+)([:<>]*)(\d*)([\+\-\*/\d]*)(.*)", str(inp))
            print(str(com.group()))
            for v in range(1, 7):
                m.append(com.group(v))
            print(m)
            if int(m[1]) == 0:
                result = "面が0の数字は振れないよ……"
            elif int(m[0]) >= 51:
                result = "回数が長すぎるとめんどくさいから振らないよ……？"
            elif int(m[0]) == 0:
                result = "えっ……回数0？　じゃあ振らなーーーーい！"
            else:
                print("○サイコロ振ります（*'∀'人）")
                for var in range(0, int(m[0])):
                    num = random.randint(1, int(m[1]))
                    num = str(num)
                    print(num)
                    if m[4] == True:
                        ad = m[4]
                    else:
                        ad = ""
                    try:
                        if ad == "":
                            dd = 0
                        else:
                            dd = int(ad)
                        if m[5] == "":
                            fd = "[" + m[3] + m[4] + "]→"
                        else:
                            fd = "[" + m[5] + "(" + m[3] + m[4] + ")]→"
                        sd = ad + fd
                        if str(m[2]) == ">":
                            if int(num) >= int(m[3]) + dd:
                                result = "ｺﾛｺﾛ……" + num + sd + "成功だよ！！"
                            else:
                                result = "ｺﾛｺﾛ……" + num + sd + "失敗だよ……"
                        else:
                            if int(num) + dd <= int(m[3]) + dd:
                                result = "ｺﾛｺﾛ……" + num + sd + "成功だよ！！"
                            else:
                                result = "ｺﾛｺﾛ……" + num + sd + "失敗だよ……"
                    except:
                        result = "ｺﾛｺﾛ……" + num
                    l.append(result)
                    n.append(int(num))
                    x += int(num)
                if ad != "":
                    x += int(ad)
                if int(m[0]) != 1:
                    result = str(n) + str(ad) + " = " + str(x)
                    l.append(result)
                print(l)
                result = '\n'.join(l)
                if len(result) > 400:
                    result = "文字数制限に引っ掛かっちゃった……"
        except:
            result = "えっ？"
        return result


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
