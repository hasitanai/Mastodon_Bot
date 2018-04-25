from mastodon import *
import time, re, sys, os, json, random, io, gc, math
import threading, requests, pprint, codecs
from time import sleep
from datetime import timedelta, datetime
from pytz import timezone  # 変更予定
import warnings, traceback
import xlrd, xlsxwriter
from xml.sax.saxutils import unescape as unesc
import asyncio
from shinagalize import shinagalize
from dateutil.tz import tzutc  # 変更予定

mastodon = None

#Winのプロンプトから起動するならこれ追加ね↓
"""
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,
                              encoding=sys.stdout.encoding,
                              errors='backslashreplace',
                              line_buffering=sys.stdout.line_buffering)
                              """
warnings.simplefilter("ignore", UnicodeWarning)

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
        text = re.sub('<p>|</p>|<a.+"tag">|<a.+"_blank">|<a.+mention">|<'
                      'span>|</span>|</a>|<span class="[a-z-]+">', "", text)
        return unesc(text, {"&apos;":"'", '&quot;':'"'})


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


class men_toot(StreamListener):
    def on_update(self, status):
        try:
            HTL.HTL(status)
            pass
        except Exception as e:
            print("エラー情報【USER】\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
            pass

    def on_notification(self, notification):
        try:
            print("===通知が来ました===")
            non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
            if notification["type"] == "mention":
                status = notification["status"]
                account = status["account"]
                mentions = status["mentions"]
                content = unesc(Re1.text(status["content"]))
                log = threading.Thread(Log(status).read())
                log.run()
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
                    elif re.compile("(アラーム|[Aa][Rr][Aa][Mm])(\d+)").search(content):
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
                        if re.compile("(アラーム|[Aa][Rr][Aa][Mm])(.*)「(.*)」").search(content):
                            mes = re.search("「(.*)」", content)
                            toot_now = ("@" + account["acct"] + " " + "（*'∀'人）時間だよーー♪♪\n"
                                        "「" + mes.group(1) + "」")
                        else:
                            toot_now = "@" + account["acct"] + " " + "（*'∀'人）時間だよーー♪♪"
                        g_vis = status["visibility"]
                        in_reply_to_id = status["id"]
                        t = threading.Timer(sec, bot.toot, [toot_now, g_vis, status['id']])
                        t.start()
                        #bot.rets(sec, toot_now, g_vis,status['id'] )
                    elif re.compile(
                                    "(フォロー|follow)(して|く[うぅー]*ださ[あぁー]*い|お願[あぁー]*い|"
                                    "おねが[あぁー]*い|頼[むみ]|たの[むみ]|ぷりーず|プリーズ|please)").search(
                                    content):
                        mastodon.account_follow(account["id"])
                        toot_now = "@" + account["acct"] + " " + "（*'∀'人）フォローしました♪♪"
                        g_vis = status["visibility"]
                        in_reply_to_id = status["id"]
                        bot.rets(8, toot_now, g_vis, status['id'])
                    elif re.compile("(こそこそ)<br />(.+)").search(content):  # 悪用されないように変えてます
                        if status["visibility"] == "direct":
                            # この機能いらなくなってきた所ある
                            """
                            print("○受け取りました")
                            com = re.search("(こそこそ).*<br />(.+)", str(content))
                            messe = com.group(2)
                            toot_now = messe
                            g_vis = "public"
                            bot.rets(1, toot_now, g_vis)
                            """
                            pass
                    elif re.compile("連想ゲーム開始").search(content):
                        if rensou_time:
                            toot_now = ("@" + account["acct"] + " "
                                        + "（*'∀'人）ごめんね、今開催中なの♪♪")
                            g_vis = status["visibility"]
                            in_reply_to_id = status["id"]
                            bot.rets(5, toot_now, g_vis, status['id'])
                        else:
                            t = threading.Timer(0, game.rensou)
                            t.start()
                            rensou_time = True
                    elif account["acct"] == "twotwo":
                        if re.compile("").search(content):
                            pass
                    elif account["acct"] == "lamazeP":
                        if re.compile("評価対象[：:]").search(content):
                            name = re.search("対象[：:]([A-Za-z0-9_]+)<br >(point|ぽいんと|ポイント)[：:](\d+)", str(content))
                            name = name.group(1)
                            point = int(name.group(3))
                            ids = status["id"]
                            bot.trial(name, point, ids)
                            pass
                    elif re.compile("ももな(図鑑|ずかん)の?([修訂]正)：.+").search(content):
                        com = re.search("ももな(図鑑|ずかん)の?([修訂]正)：(.+)", str(content))
                        tx = com.group(2)
                        bot.toot("@lamazeP ももな図鑑の訂正要望が来たよ！！\n:@{0}: 「{1}」".format(account["acct"], tx), "direct", status["id"])
                    else:
                        pass
                v = threading.Timer(5, bot.fav_now,[status["id"]])
                v.start()
            elif notification["type"] == "favourite":
                account = notification["account"]
                print(str(account["display_name"]).translate(non_bmp_map) + "@" + str(
                    account["acct"]) + "からニコってくれたよ₍₍ ◝(●˙꒳˙●)◜ ₎₎")
                print()
                bot.thank(account, 32)
                print("---")
            elif notification["type"] == "reblog":
                account = notification["account"]
                print(str(account["display_name"]).translate(non_bmp_map) + "@" + str(
                    account["acct"]) + "がブーストしてくれたよ(๑˃́ꇴ˂̀๑)")
                print()
                bot.thank(account, 32)
                print("---")
            pass
        except Exception as e:
            print("エラー情報【USER】\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
            pass


class res_toot(StreamListener):
    def on_update(self, status):
        try:
            print("===タイムライン===")
            log = threading.Thread(Log(status).read())
            log.run()
            Log(status).write()
            ltl = threading.Thread(LTL.LTL(status))
            ltl.run()
            print("   ")
            pass
        except Exception as e:
            print("エラー情報【LOCAL】\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
            pass

    def on_delete(self, status_id):
        print(str("===削除されました【{}】===").format(str(status_id)))


class HTL():
    def HTL(status):
        account = status["account"]
        ct = account["statuses_count"]
        if account["acct"] == "JC":
            path = 'thank\\' + account["acct"] + '.txt'
            if os.path.exists(path):
                f = open(path, 'r')
                x = f.read()
                f.close()
                ct += 1
                if re.match('^\d+000$', str(ct)):
                    toot_now = "°˖✧◝(⁰▿⁰)◜✧˖" + str(ct) + 'toot達成ーーーー♪♪'
                    g_vis = "public"
                    bot.rets(4, toot_now, g_vis)
        else:
            bot.check03(status)


class LTL():
    def LTL(status):  # ここに受け取ったtootに対してどうするか追加してね（*'∀'人）
        # 以下bot機能の一覧
        bot.check01(status)
        bot.fav01(status)
        bot.fav02(status)
        bot.res01(status)
        bot.res02(status)
        bot.res03(status)
        bot.res04(status)
        bot.res05(status)
        bot.check00(status)
        bot.check02(status)
        game.poem(status)
        game.senryu(status)
        game.cinema(status)
        game.prof(status)
        game.quest(status)
        # ここまで

class bot():
    def _init_(self):
        pass

    def res(sec):
        count.end = count.end - sec
        if count.end < 0:
            count.end = 0

    def rets(sec, toot_now, g_vis, rep=None, spo=None):
        now = time.time()
        delay = now - count.CT
        loss = count.end - int(delay)
        if loss < 0:
            loss = 0
        ing = sec + loss
        t = threading.Timer(ing, bot.toot, [toot_now, g_vis, rep, spo])
        t.start()
        print("【次までのロスタイム:" + str(count.end+sec) + "】")
        s = threading.Timer(ing, bot.res, [sec])
        s.start()
        del t
        del s
        gc.collect()
        count.CT = time.time()
        count.end = ing

    def toot(toot_now, g_vis, rep=None, spo=None):
        mastodon.status_post(status=toot_now,
                             visibility=g_vis,
                             in_reply_to_id=rep,
                             spoiler_text=spo)
        print("【次までのロスタイム:" + str(count.end) + "】")
        """
        visibility これで公開範囲を指定できるよ！: public, unlisted, private, direct
        """

    def standby():
        print("「(๑•̀ㅁ•́๑)✧＜tootｽﾃﾝﾊﾞｰｲ」")

    def block01(status):
        account = status["account"]
        content = status["content"]
        with codecs.open("NG\sekuhara.txt", 'r', 'utf-8') as f:
            l = []
            for x in f:
                l.append(x.rstrip("\r\n"))
        m = len(l)
        for x in range(0, m):
            if re.compile(str(l[x])).search(re.sub("<p>|</p>", "", str(status))):
                j = True
                print("う～う～！セクハラ検出しました！　→" + str(l[x]))
                bot.toot("@lamazeP (｡>﹏<｡)これってセクハラですか？？\n:@{0}: 「{1}」".format(str(account["acct"]),
                         str(content)), "direct", status["id"])
                bot.thank(account, -64)
                break
            else:
                j = False
        return j

    def block02(status):
        account = status["account"]
        content = status["content"]
        with codecs.open("NG\\bougen.txt", 'r', 'utf-8') as f:
            l = []
            for x in f:
                l.append(x.rstrip("\r\n"))
        m = len(l)
        for x in range(0, m):
            if re.compile(str(l[x])).search(re.sub("<p>|</p>", "", str(status))):
                j = True
                print("う～う～！暴言検出しました！　→" + str(l[x]))
                bot.toot("@lamazeP (｡>﹏<｡)こちらはですか？？\n:@{0}: 「{1}」".format(str(account["acct"]),
                         str(content)), "direct", status["id"])
                bot.thank(account, -64)
                break
            else:
                j = False
        return j

    def trial01(name, point, ids): # デバック用
        path = 'thank\\' + name + '.txt'
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
            toot_now = ("（*'∀'人）評価しておいたよ\n対象ID：{0} :@{0}:".format(name))
        else:
            toot_now = ("(｡>﹏<｡)会ったことのない人みたいだから評価できなかったよ")
        bot.toot(toot_now, "direct", ids)
        pass

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
                pass
            else:
                if re.match('^\d+0000$', str(ct)):
                    toot_now = (" :@" + account['acct'] + ": @" +
                                account['acct'] + "\n°˖✧◝(⁰▿⁰)◜✧˖" + str(ct) +
                                'tootおめでとーーーー♪♪')
                    g_vis = "public"
                    bot.rets(4, toot_now, g_vis)
                elif re.match('^\d000$', str(ct)):
                    toot_now = (" :@" + account['acct'] + ": @" +
                                account['acct'] + "\n（*'∀'人）" + str(ct) +
                                'tootおめでとーー♪')
                    g_vis = "public"
                    bot.rets(4, toot_now, g_vis)
        else:
            pass

    def check01(status):
        account = status["account"]
        created_at = status['created_at']
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        with codecs.open('acct\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:  # 書き込みモードで開く
            f.write(str(status["account"]).translate(non_bmp_map))  # アカウント情報の更新
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
        with codecs.open('at_time\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:  # 書き込みモードで開く
            f.write(str(status["created_at"]))  # \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z

    def check03(status):
        account = status["account"]
        ct = account["statuses_count"]
        if account["acct"] == "Knzk":  # 神崎おにいさん監視隊
            ct += 5
            if re.match('^\d+000$', str(ct)):
                toot_now = "@Knzk (๑•̀ㅁ•́๑)神崎おにいさん！！\n" + str(ct) + 'tootまであと5だよ！！！！'
                g_vis = "direct"
                bot.rets(4, toot_now, g_vis)
        elif account["acct"] == "5":  # やなちゃん監視隊
            ct += 5
            if re.match('^\d+0000$', str(ct)):
                toot_now = "@5 (๑•̀ㅁ•́๑)やなちゃん！！\n" + str(ct) + 'tootまであと5だよ！！！！'
                g_vis = "direct"
                bot.rets(4, toot_now, g_vis)
        elif account["acct"] == "yzhsn":  # 裾野監視隊
            ct += 5
            if re.match('^\d+000$', str(ct)):
                toot_now = "@yzhsn (๑•̀ㅁ•́๑)おい裾野！！\n" + str(ct) + 'tootまであと5だよ！！！！'
                g_vis = "direct"
                bot.rets(4, toot_now, g_vis)
        elif account["acct"] == "lamazeP":  # ラマーズＰ監視隊
            ct += 5
            if re.match('^\d+000$', str(ct)):
                toot_now = "@lamazeP (๑•̀ㅁ•́๑)" + str(ct) + 'tootまであと5だよ！！！！'
                g_vis = "direct"
                bot.rets(4, toot_now, g_vis)
        else:  # テスト
            ct += 5
            if re.match('^\d+000$', str(ct)):
                toot_now = ("@" + account["acct"] +
                            " (๑•̀ㅁ•́๑)ただいまフォローしてる方にお知らせだよ！\n" + str(ct) +
                            'tootまであと5だよ！！！！')
                g_vis = "direct"
                bot.rets(4, toot_now, g_vis)

    def res01(status):
        account = status["account"]
        content = re.sub("<p>|</p>", "", str(status['content']))
        path = 'thank\\' + account["acct"] + '.txt'
        try:
            with codecs.open('date\\adana\\' + account["acct"] + '.txt', 'r', 'UTF-8') as f:
                name = f.read()
        except:
            if account['display_name'] == "":
                name = account['acct']
            else:
                name = re.sub("[(:（].+[):）]|@[a-zA-Z0-9_]+|\s|＠.+", "", account['display_name'])
        if os.path.exists(path):
            f = open(path, 'r')
            x = f.read()
            f.close()
        if int(x) >= -10:
            if account["acct"] != "JC" and account["acct"] != "kiri_bot01":
                if count.timer_hello == 0:
                    if re.compile("ももな(.*)おは|ももな(.*)おあひょ").search(content):
                        print("○hitしました♪")
                        print("○あいさつします（*'∀'人）")
                        toot_now = "(๑•̀ㅁ•́๑)✧おはありでーーーーす♪" + "\n#ニコフレ挨拶部"
                        g_vis = "public"
                        bot.rets(20, toot_now, g_vis)
                        count.timer_hello = 1
                else:
                    if re.compile("[寝ね](ます|る|マス)([よかぞね]?|[…。うぅー～！・]+)$|^[寝ね](ます|る|よ)[…。うぅー～！・]*$|"
                                  "[寝ね](ます|る|マス)(.*)[ぽお]や[ユすしー]|ももな(.*)[ぽお]や[ユすしー]|"
                                  "(そろそろ|やっと|ようやく|[ね寝]([～ー]|る[～ー]))寝").search(content):
                        if not re.compile("[寝ね]る(かた|方|人|ひと|民)|あやねる").search(status['content']):
                            print("○hitしました♪")
                            print("○おやすみします（*'∀'人）")
                            if account['acct'] == "5":  # やなちゃん専用挨拶
                                print("○やなちゃんだ！！（*'∀'人）")
                                posting = '(｡>﹏<｡)あとで一緒に寝るーーーー！！！！'
                            else:
                                posting = '(ृ 　 ु *`ω､)ु ⋆゜おやすみーーーー♪'
                            toot_now = (":@{0}: {1}\n{2}\n#ニコフレ挨拶部".format(account['acct'], name, posting))
                            bot.rets(6, toot_now, "public")
                    elif re.compile("([いイ行逝]って|出かけて|(風呂|ふろ).*(入|はい)って)(くる|きま([あぁー]*す|[きキ]マストドン|$))[^？\?]|"
                                    "おでかけ(する|しま([あぁー]*す|[しシ]マストドン|$))[^？\?]|(ふろ|風呂)って(くる|きま(す|$))|"
                                    "(出勤|離脱|しゅっきん|りだつ)(する[^な]|しま([あぁー]*す[^？\?]|[しシ]マストドン|$))|"
                                    "(出勤|離脱)([。っ！]*$|しま$)|(.+)して?(くる|きま([あぁー]*す[^？\?]|$)|[きキ]マストドン)([ー～！。よぞね]|$)|"
                                    "(仕事|しごと).*(戻|もど)(る|りゅ|りま([すつ]|$))|(飯|めし)って(くる|きま(す|$))|(めし|飯)([い行]く|[お落]ち)|"
                                    "^りだつ$"
                                    ).search(content):
                        print("○hitしました♪")
                        print("○見送ります（*'∀'人）")
                        if account['acct'] == "5":  # やなちゃん専用挨拶
                            print("○やなちゃんだ！！（*'∀'人）")
                            posting = '(*>_<*)ﾉいってらいってらーーーー！！！！'
                        else:
                            posting = 'いってらーーーー！！'
                        toot_now = (":@{0}: {1}\n{2}\n#ニコフレ挨拶部".format(account['acct'], name, posting))
                        bot.rets(6, toot_now, "public")
                    elif re.compile("ただいま(です|[！あー～。…]*(<br/ >|$)|(もど|戻)(ってきた|った|りました))|ただいマストドン"
                                    "|(おうち|家).*([着つ]いた|帰った|帰ってきた)|(帰宅|きたく)(した|しました|$)|ほかいま|"
                                    "^ただいま|(飯|めし|ふろ|風呂|シャワー).*(もど|戻)ってき(た|ました)|ほかってき(た|ました)").search(content):
                        print("○hitしました♪")
                        print("○優しく迎えます（*'∀'人）")
                        if account['acct'] == "5":  # やなちゃん専用挨拶
                            print("○やなちゃんだ！！（*'∀'人）")
                            posting = '٩(๑❛ᴗ❛๑)۶おかえりおかえりーー！！'
                        else:
                            posting = '( 〃 ❛ᴗ❛ 〃 )おかえりおかえりーー！！'
                        toot_now = (":@{0}: {1}\n{2}\n#ニコフレ挨拶部".format(account['acct'], name, posting))
                        bot.rets(6, toot_now, "public")
                    else:
                        try:  # 新しいVerに向けてコードを組まないといけない…… 
                            with codecs.open('at_time\\' + account["acct"] + '.txt', 'r', 'UTF-8') as f:
                                nstr = f.read()
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
                                    posting = "(｡>﹏<｡)暫く会えなくて寂しかったよーーーー！！！！"
                                else:
                                    posting = "（*'∀'人）おひさひさーーーー♪"
                                
                                toot_now = (":@{0}: {1}\n{2}".format(account['acct'], name, posting))
                                bot.rets(6, toot_now, "public")
                            elif delta.total_seconds() >= 10800:
                                if now_time.hour in range(3, 9):
                                    posting = bot.rand_w('time\\kon.txt')
                                elif now_time.hour in range(9, 19):
                                    posting = bot.rand_w('time\\kob.txt')
                                else:
                                    posting = bot.rand_w('time\\oha.txt')
                                if account['acct'] == "5":  # やなちゃん専用挨拶
                                    print("○やなちゃんだ！！（*'∀'人）")
                                    name = "やなちゃん！！！！！！"
                                    # elif account['acct'] == "lamazeP":  # ジョーク
                                    #     print("○ジョークを言います（*'∀'人）")
                                    #     name = "初めましてチノちゃん！！"
                                    #     posting = 'ようこそようこそーーーー♪'
                                else:
                                    print("○あいさつします（*'∀'人）")
                                    pass
                                toot_now = (":@{0}: {1}\n{2}\n#ニコフレ挨拶部".format(account['acct'], name, posting))
                                bot.rets(6, toot_now, "public")
                        
                        except:
                            print("○初あいさつします（*'∀'人）")
                            try:
                                v = threading.Timer(2, mastodon.status_reblog,[status["id"]])
                                v.start()
                                jc = mastodon.acount("5667")
                                ct = jc["statuses_count"]
                                ct += 1
                            except:
                                print("○失敗しました")
                                pass
                            if account['statuses_count'] <= 2:
                                if account['display_name'] == "":
                                    name = account['acct']
                                else:
                                    name = account['display_name']
                                posting = 'ようこそようこそーーーー♪'
                                shinki = True
                            else:
                                if account['display_name'] == "":
                                    name = account['acct']
                                else:
                                    name = account['display_name']
                                posting = 'いらっしゃーーーーい♪'
                                shinki = False
                            toot_now = (":@{0}: @{0}\n{1}\n{2}\n#ニコフレ挨拶部".format(account['acct'], name, posting))
                            bot.rets(6, toot_now, "public")
                            if shinki is True:
                                bot.toot("@lamazeP 新規さんが来たよーー（小声）\n【" + str(account['acct']) + "】",
                                         "direct", status["id"])
                            try:
                                if re.match('^\d+000$', str(ct)):
                                        toot_now = "°˖✧◝(⁰▿⁰)◜✧˖" + str(ct) + 'toot達成ーーーー♪♪'
                                        g_vis = "public"
                                        bot.rets(4, toot_now, g_vis)
                            except:
                                print("○キリ番に気づいていないようです")
                                pass
        else:
            print("○反応がない人なので挨拶しません（*'∀'人）")

    def res02(status):
        account = status["account"]
        content = Re1.text(status["content"])
        if account["acct"] != "JC":
            matches = re.search("([^>]+)とマストドン(どちら|どっち)が大[切事]か[分わ]かってない", content)
            if matches:
                print("○hitしました♪")
                sekuhara = bot.block01(status)
                bougen = bot.block02(status)
                if len(content) > 60:
                    toot_now = "٩(๑`^´๑)۶長い！！！！！！"
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)
                else:
                    if sekuhara:
                        print("○セクハラサーチ！！")
                        toot_now = "そんなセクハラ分かりません\n(* ,,Ծ‸Ծ,, )ﾌﾟｰ"
                    elif bougen:
                        print("○暴言サーチ！！")
                        toot_now = "(｡>﹏<｡)暴言怖いよぉ……"
                    else:
                        print("○だったら")
                        shinagalized_text = shinagalize(matches.group(1))
                        toot_now = ":@" + account["acct"] + ":" + shinagalized_text + "マストドンして❤"
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)

    def res03(status):
        account = status["account"]
        if account['acct'] != "kiri_bot01":
            if account["acct"] != "JC":
                if re.compile("ももな([^\d]*)[1-5][dD]\d+").search(status['content']):
                    print("○hitしました♪")
                    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
                    coro = Re1.text(str(status['content']).translate(non_bmp_map))
                    toot_now = ":@" + account["acct"] + ": @" + account["acct"] + "\n" + game.dice(coro)
                    bot.rets(8, toot_now, status["visibility"])
                elif re.compile("ももな(.*)([6-9]|\d{2})[dD](\d*)").search(status['content']):
                    toot_now = "@{} ６回以上の回数は畳む内容だからメンションの方で送ってーー！！".format(account["acct"])
                    bot.rets(6, toot_now, status["visibility"], status["id"])

    def res04(status): #あだ名実装
        account = status["account"]
        profile_emojis = status["profile_emojis"]
        if account["acct"] != "JC":
            data_dir_path = u"./thank/"
            abs_name = data_dir_path + '/' + account["acct"] + '.txt'
            with open(abs_name, 'r')as f:
                x = f.read()
                y = int(x)
            if re.compile("ももな.*あだ[名な][｢「](.+)[」｣]って呼んで").search(status['content']):
                if y >= 0:
                    print("○hitしました♪")
                    ad = re.search("ももな.*あだ[名な][｢「](.+)[」｣]って[呼よ]んで", status['content'])
                    name = ad.group(1)
                    adan = Re1.text(name)
                    adan = re.sub(':', '', adan)
                    adan = re.sub('@[a-zA-Z0-9_]+', ':\1:', adan)
                    sekuhara = bot.block01(status)
                    bougen = bot.block02(status)
                    if len(adan) > 60:
                        toot_now = "٩(๑`^´๑)۶長い！！！！！！"
                    else:
                        if sekuhara:
                            toot_now = "(｡>﹏<｡)そんないやらしい呼び方出来ないよーー……"
                        elif bougen:
                            toot_now = "(｡>﹏<｡)ふぇぇ暴言怖いよーー……"
                        else:
                            with codecs.open('date\\adana\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:
                                f.write(adan)
                            toot_now = "@{1} ٩(๑> ₃ <)۶分かったーーーー！！\n「{0}」って呼ぶようにするね！！".format(adan, account["acct"])
                    bot.rets(6, toot_now, status["visibility"], status["id"])
            elif re.compile("ももな.*:@([A-Za-z0-9_]+): ?(さん)?のこと.*[｢「](.+)[」｣]って[呼よ]んで").search(status['content']):
                ad = re.search("ももな.*:@([A-Za-z0-9_]+): ?のこと.*[｢「](.+)[」｣]って[呼よ]んで", status['content'])
                acct = ad.group(1)
                print("○hitしました♪")
                if y >= 50000 or account["acct"] == "lamazeP": 
                    name = ad.group(2)
                    adan = Re1.text(name)
                    adan = re.sub(':', '', adan)
                    adan = re.sub('@[a-zA-Z0-9_]+', ':\1:', adan)
                    sekuhara = bot.block01(status)
                    bougen = bot.block02(status)
                    if acct == account["acct"]:
                        if sekuhara:
                            toot_now = "(｡>﹏<｡)そんないやらしい呼び方出来ないよーー……"
                        elif bougen:
                            toot_now = "(｡>﹏<｡)ふぇぇ暴言怖いよーー……"
                        else:
                            with codecs.open('date\\adana\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:
                                f.write(adan)
                            toot_now = ("@{1} ٩(๑> ₃ <)۶分かったーーーー！！\n「{0}」って呼ぶようにするね！！"
                                        "#ももなのあだ名事情".format(adan, account["acct"]))
                    elif len(adan) > 60:
                        toot_now = "٩(๑`^´๑)۶長い！！！！！！"
                    else:
                        try:
                            abs_it = data_dir_path + '/' + acct + '.txt'
                            with open(abs_it, 'r')as f:
                                x = f.read()
                                z = int(x)
                            if not sekuhara:
                                if account["acct"] == "lamazeP":
                                    y =+ 1000000000
                                if z <= y:
                                    with codecs.open('date\\adana\\' + acct + '.txt', 'w', 'UTF-8') as f:
                                        f.write(adan)
                                    toot_now = (":@" + account['acct'] + ": ٩(๑> ₃ <)۶分かったーーーー！！\n"
                                                ":@{1}:のことは「{0}」って呼ぶようにするね！！"
                                                "#ももなのあだ名事情".format(adan, acct))
                                else:
                                    toot_now = ":@" + account['acct'] + ": (｡>﹏<｡):@{}:のあだ名変えたくないよ！！！！".format(acct)
                            else:
                                toot_now = ":@" + account['acct'] + ": (｡>﹏<｡)いくら仲が良くてもそれは出来ないよ！！！！"
                        except:
                            toot_now = ":@" + account['acct'] + " :( ◉ ‸ ◉ )私の知らない人だから無理……"
                else:
                    toot_now = ":@" + account['acct'] + ": (｡>﹏<｡)もう少し仲良くならないと呼びかけられないよ！！"
                bot.rets(6, toot_now, "public")
            elif re.compile("ももな.*あだ[名な](キャンセル|消して)").search(status['content']):
                print("○hitしました♪")
                name = re.sub("[(:（].+[):）]|@[a-zA-Z0-9_]+|\s|＠.+", "", account['display_name'])
                with codecs.open('date\\adana\\' + acct + '.txt', 'w', 'UTF-8') as f:
                    f.write("")
                toot_now = ("@{} ٩(๑> ₃ <)۶分かったーーーー！！\n次からは普通に呼びかけるね！！".format(account["acct"]))
                bot.rets(6, toot_now, status["visibility"], status["id"])
            elif re.compile("ももな.*:@([A-Za-z0-9_]+): ?のあだ[名な](を?教えて|(って|は)何)").search(status['content']):
                ad = re.search("ももな.*:@([A-Za-z0-9_]+): ?のあだ[名な](を?教えて|(って|は)何)", status['content'])
                acct = ad.group(1)
                print("○hitしました♪")
                try:
                    with codecs.open('date\\adana\\' + account["acct"] + '.txt', 'r', 'UTF-8') as f:
                        name = f.read()
                    toot_now = (":@{1}:のあだ名は「{0}」だよ！！！！".format(name, account["acct"]))
                except:
                    toot_now = (":@{}:のあだ名は設定してないよ！！！！".format(account["acct"]))
                bot.rets(6, toot_now, "public")

    def res05(status):  # t.co警察とか
        account = status["account"]
        content = Re1.text(status["content"])
        if re.search('href="(?:[^a-z0-9_-]|^)t\.co/[a-zA-Z0-9]', status["content"]):
            if account["acct"] != "JC":
                if count.t == False:
                    print("○hitしました♪")
                    toot_now = ("t.co！？".format(account["acct"]))
                    bot.rets(2, toot_now, "public")
                    count.t = True
                    def cool():
                        count.t = False
                    t = threading.Timer(90, cool)
                    t.start()
                else:
                    print("○t.coしつこい٩(๑`^´๑)۶")
                bot.thank(account, -64)
        elif re.compile("なんでも|何でも|ナンデモ|ナンでも").search(content):
            if count.n == False:
                print("○hitしました♪")
                toot_now = ("ん？".format(account["acct"]))
                bot.rets(2, toot_now, "public")
                count.n = True
                def cool():
                    count.n = False
                t = threading.Timer(180, cool)
                t.start()
    
    def fav01(status):
        account = status["account"]
        if re.compile("(ももな|:@JC:|ちゃんもも|:nicoru\d*:|\WJC\W|もなな)").search(status['content']):
            bot.thank(account, 8)
            v = threading.Timer(5, bot.fav_now,[status["id"]])
            v.start()

    def fav02(status):
        account = status["account"]
        if re.compile("(ラマーズ[PpＰｐ]|[Ll]amaze[Pp])").search(status['content']):
            bot.thank(account, 10)
            v = threading.Timer(5, bot.fav_now,[status["id"]])
            v.start()
            
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

    def fav_now(fav):  # ニコります
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
                f.write("\n\n【" + str(jst_now) + "】\n")
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
                f.write("\n\n【" + str(jst_now) + "】\n")
                traceback.print_exc(file=f)
            sleep(180)
            bot.t_user()
            pass


class game():
    def emo(user):
        data_dir_path = u"./thank/"
        file_list = os.listdir(r'./thank/')
        abs_name = data_dir_path + '/' + user + '.txt'
        with open(abs_name, 'r') as f:
            x = f.read()
        return x
    
    def fav(id):
        mastodon.status_favourite(id)

    def prof(status):
        account = status["account"]
        content = Re1.text(status["content"])
        profile_emojis = status["profile_emojis"]
        if account["acct"] != "JC":
            spo = None
            if re.compile("ももな.*:@([A-Za-z0-9_]+): ?(さん)?(は|って)こんな(人|ひと|やつ|奴|方).*[：:]").search(content):
                print("○hitしました♪")
                word = re.search("ももな.*:@([A-Za-z0-9_]+): ?(さん)?(は|って)こんな(人|ひと|やつ|奴|方).*[：:](<br />)?(.+)", str(content))
                acct = word.group(1)
                tex1 = word.group(6)
                over = False
                user_check = False
                for x in profile_emojis:  # ユーザー絵文字検出器～～ﾟ+.･ﾟ+｡(〃・ω・〃)｡+ﾟ･.+ﾟ
                    if x["shortcode"] == ("@{}".format(acct)):
                        print("○ユーザーを確認しました♪")
                        user_check = True
                        break
                if user_check == True:
                    if len(tex1) > 60:
                        toot_now = "٩(๑`^´๑)۶文章が長い！！！！"
                    else:
                        tex2 = tex1 + "（by:@{}:）".format(account["acct"])
                        try:
                            with open("game\\prof\\{}.txt".format(acct),"r") as f:
                                tex0 = f.read()
                            with open("game\\prof\\{}.txt".format(acct),"r") as f:
                                tex0s = f.readlines()
                            resch = "^.*（by:@{}:）\n".format(account["acct"])
                            tex3 = ""
                            for x in tex0s:
                                print(x)
                                if re.search(resch, x):
                                    over = True
                                else:
                                    tex3 = tex3 + x
                            try:
                                with open("game\\prof\\{}.txt".format(acct), "w") as f:
                                    print(tex3)
                                    f.write(tex3)
                                print("○上書きしたよ！！！！")
                            except:
                                with open("game\\prof\\{}.txt".format(acct), "w") as f:
                                    f.write(tex0)
                                print("○上書きできなかったよ……")
                            if len(tex0) > 400:
                                toot_now = ("これ以上:@{}:のこと覚えられないよ……整頓するからもう少し待ってね(｡>﹏<｡)".format(acct))
                                bot.rets(6, toot_now, "public")
                            elif re.search("[^:]?@[A-Za-z0-9_]+[^:]?", tex1):
                                 toot_now = ("٩(๑`^´๑)۶リプライのいたずらしちゃダメ！！！！")
                                 count.emo03(account["acct"], -64)
                            else:
                                with open("game\\prof\\{}.txt".format(acct),"a") as f:
                                    f.write(tex2+"\n")
                                if over == True:
                                    toot_now = (":@{0}:ありがと！！\n:@{1}:のこと、覚え直した！！！！".format(account["acct"], acct)+"\n#ももな図鑑")
                                else:
                                    toot_now = (":@{0}:ありがと！！\n:@{1}:の知ってること、また一つ覚えた！！！！".format(account["acct"], acct)+"\n#ももな図鑑")
                        except:
                            with open("game\\prof\\{}.txt".format(acct),"a") as f:
                                f.write(tex2+"\n")
                            toot_now = (":@{0}:ありがと！！\n:@{1}:のこと覚えた！！！！".format(account["acct"], acct)+"\n#ももな図鑑")
                else:
                    toot_now = (":@{}:は実在しない人だよ……(｡>﹏<｡)".format(acct) + "\n#ももな図鑑")
                bot.rets(6, toot_now, "public")
            elif re.compile("ももな.*:@([A-Za-z0-9_]+): ?(さん)?((について|の(こと|事))(教|おし)[えへ]て|って[誰何])").search(content):
                print("○hitしました♪")
                word = re.search("ももな.*:@([A-Za-z0-9_]+): ?(さん)?((について|の(こと|事))(教|おし)[えへ]て|って[誰何])", str(content))
                acct = word.group(1)
                try:
                    with open("game\\prof\\{}.txt".format(acct),"r") as f:
                        tex0 = f.read()
                        spo = ":@{}:はこんな人だよ！！".format(acct)
                    try:
                        with codecs.open('date\\adana\\' + acct + '.txt', 'r', 'UTF-8') as f:
                            name = f.read()
                            adan = name + "だよ！！"
                    except:
                        adan = "まだないみたいだよ！！"
                    toot_now = (tex0 + "\nあだ名は{}".format(adan)+"\n#ももな図鑑")
                except:
                    toot_now = ("(｡>﹏<｡)ごめんね……:@{}:がどんな人なのか分からないの……".format(acct)+"\n#ももな図鑑")
                bot.rets(6, toot_now, "public", spo=spo)
                

    def cinema(status):
        account = status["account"]
        content = Re1.text(status["content"])
        gameIn = ("(劇場|げきじょう|[Cc]inema|シネマ)(ゲーム|げーむ)[：:]"+
                  "\n【(.+)】\n起[：:](.+)\n承[：:](.+)\n転[：:](.+)\n結[：:](.+)")
        gameOut = "(劇場|げきじょう|[Cc]inema|シネマ)(ゲーム|げーむ)"+".*(ひとつ|おねが[いひ]|お願[いひ]|[1１一]つ)"
        if re.compile(gameIn).search(content):
            print("○hitしました♪")
            word = re.search(gameIn+"(\n.*)?", str(content))
            sekuhara = bot.block01(status)
            if sekuhara:
                bot.rets(5, "٩(๑`^´๑)۶えっちなのはよくない！！！！", "public")
            else:
                Title = word.group(3)
                Ki = word.group(4)
                Sho = word.group(5)
                Ten = word.group(6)
                Kets = word.group(7)
                if len(Ki) > 80 or len(Sho) > 80 or len(Ten) > 80 or len(Kets) > 80 or len(Title) > 60:
                    bot.rets(5, "٩(๑`^´๑)۶長い！！！！！！", "public")
                    pass
                else:
                    f = codecs.open('game\\cinema_word.txt', 'a', 'UTF-8')
                    f.write(Title+">>"+Ki+">>"+Sho+">>"+Ten+">>"+Kets+">>"+account["acct"]+"\r\n" )
                    f.close()
                    v = threading.Timer(5, game.fav, [status["id"]])
                    v.start()
                    print("◆　成功しました(∩´∀｀)∩　◆")
            return
        elif re.compile("ももな.*"+gameOut).search(content):
            if account["acct"] != "JC":
                f = codecs.open('game\\cinema_word.txt', 'r', 'utf-8')
                word1 = []
                for x in f:
                    word1.append(x.rstrip("\r\n").replace('\\n', '\n'))
                f.close()
                m = len(word1)
                word2 = []
                name = []
                for x in range(5):
                    s = random.randint(0, m-1)
                    word2.append((word1[s]).split('>>'))
                c0 = word2[0]
                c1 = word2[1]
                c2 = word2[2]
                c3 = word2[3]
                c4 = word2[4]
                c5 = [c0[5],c1[5],c2[5],c3[5],c4[5]]
                cast = list(set(c5[1:]))
                toot_now = ("【タイトル】\n"+unesc(c0[0])+"\n\n【あらすじ】\n"+unesc(c1[1])+
                            "\n"+unesc(c2[2])+"\n"+unesc(c3[3])+"\n"+unesc(c4[4])+"\n\n"
                            "【スタッフ】\n監督：:@"+c0[5]+":\n主演キャスト：:@"+str("::@".join(cast)))+ ":\n#劇場げーむ"
                spo = ":@" + account["acct"] + ":さんに上映開始のお知らせ"
                return bot.rets(6, toot_now, "public", None, spo)


    def world(status):  # 使われない機能……
        account = status["account"]
        content = Re1.text(status["content"])
        hitting = 'セカイが(.+)になっちゃ(っ[たて]|いま[すし])'
        if re.compile(hitting).search(content):
            wrd = re.search(hitting, str(content))
            toot_now = 'セカイが' + wrd(1) + 'になっちゃった♪'
            bot.rets(5, toot_now, "public")
        else:
            pass

    def quest(status):  # 連想ゲームをボツにして変わりの予定
        account = status["account"]
        content = Re1.text(status["content"])
        profile_emojis = status["profile_emojis"]
        if account["acct"] != "JC":
            if re.compile("ももな.*:@([A-Za-z0-9_]+): ?の戦闘力を?(教[へえ][てろ]|おし[へえ][てろ]|おねが[ひい]|お願[ひい]|表示)").search(content):
                word = re.search("ももな.*:@([A-Za-z0-9_]+): ?の戦闘力を?(教[へえ][てろ]|おし[へえ][てろ]|おねが[ひい]|お願[ひい]|表示)", str(content))
                acct = word.group(1)
                user_check = False
                for x in profile_emojis:  # ユーザー絵文字検出器～～ﾟ+.･ﾟ+｡(〃・ω・〃)｡+ﾟ･.+ﾟ
                    if x["shortcode"] == ("@{}".format(acct)):
                        print("○ユーザーを確認しました♪")
                        it = mastodon.account(int(x['account_id']))
                        user_check = True
                        break
                if user_check == True:
                    ex = int(it["statuses_count"])
                    if 0 == it["statuses_count"]:
                        toot_now = 'まだ冒険してない新規さんだよ！！'
                    else:
                        p = math.sqrt(7.298555)  # 平方根の処理だよ！
                        for x in range(1,101):
                            e = int(pow(x-1,p)*p)+(10*x) 
                            if e < ex:
                                pass
                            else:
                                xx = e - ex
                                lv = x
                                break
                        ak = int(it["followers_count"]/3)+int(lv*it["followers_count"]/400)+lv
                        df = int(it["following_count"]/3)+int(lv*it["followers_count"]/400)+lv
                        hp = int(((df/60)+lv) * (int(ex / 1000)+1))
                        mn = int(min(it["followers_count"], it["following_count"]))
                        mx = int(max(it["followers_count"], it["following_count"]))
                        mp = int(max(mn-((mx-mn)/8), 0))
                        try:
                            g = int(game.emo(it["acct"]))
                            if g < 0:
                                g = 0
                            a = datetime.strptime(re.sub("Z","", status['created_at']), '%Y-%m-%dT%H:%M:%S.%f')
                            a = a.replace(tzinfo=tzutc())
                            b = it['created_at']
                            d = a - b
                            ra = int(math.sqrt(d.days/ex)*10) + int(it["followers_count"]/1000)
                            if ra >= 20:
                                ra = "20(MAX)"
                            toot_now = (":@{0}:の戦闘力だよ！！\nLv：{1}　レア度：{2}\n"
                                        "攻撃力：{3}\n防御力：{4}\n"  # "かしこさ：{9}\nみりょく：{10}\n"
                                        "HP：{5}　MP：{6}\n所持金：{7}\n次のLvまで{8}tootだよ！！").format(
                                            acct, lv, ra, ak, df, hp, mp, g, xx)
                            toot_now = toot_now+"\n#ももなクエスト"
                        except FileNotFoundError:
                            toot_now = "まだ会ったことがない人だからわからないの(｡>﹏<｡)"
                else:
                    toot_now = '¿?(๑ºㅅº๑)¿?この世に存在しない人だよ！！！！'
                    pass
                bot.rets(5, toot_now, "public")
        pass

    def count(user):
        i = 0
        f = 0
        b = 0
        u = mastodon.account(user)
        print(u['username'])
        c = mastodon.account_statuses(user,limit=25)
        for x in range(3):
            d = mastodon.account_statuses(user, max_id=(c[-1])["id"], limit=25)
            for x in d:
                c.append(x)
        for x in c:
            f = f + x['favourites_count']
            b = b + x['reblogs_count']
            i = i + 1
            print(x["id"],x['favourites_count'],x['reblogs_count'])

        print(f)
        print(b)
        f = f/i
        b = b/i
        s = {'fav率':f , 'reb率':b}
        print("拾った回数：{}".format(i))
        return s

    def quiz(status):
        account = status["account"]
        content = Re1.text(status["content"])
        if re.compile("クイズ(問題|もんだい)[：:]<br />").search(content):
            try:
                qz = re.search("クイズ(問題|もんだい)[：:]<br />[QqＱｑ][.．](.+)<br />"
                               "[AaＡａ][.．](.+)", str(content))
                #ファイル読み書きモードで呼び出し
                try:
                    with open("game\\quiz.json","r") as f:
                        quiz = json.load(f)
                except:
                    quiz = {}
                #lenを確認して番号振り
                ("{0}{1}: {2}").format(account["acct"],qz.group(2)+">>>"+qz.group)
                #書き出し処理＆保存
                with open("game\\quiz.json","w") as f:
                    json.dump(quiz,f)
                return ("クイズ問題、登録しました（*'∀'人）\n"
                        "問題番号"+ "xxx")
            except:
                return "クイズ問題、登録に失敗しました(｡>﹏<｡)"
                pass
            pass
        elif re.compile("クイズ(回答|解答|かいとう)[：:]<br />").search(content):
            ans = re.search("クイズ(回答|解答|かいとう)[：:]<br />[QqＱｑ][.．](.+)<br />"
                            "[AaＡａ][.．](.+)", str(content))
            pass

    def memo(status):
        account = status["account"]
        content = Re1.text(status["content"])
        if re.compile("ももな.*(メモ|めも)[：:]").search(content):
            try:
                memo = re.search("ももな.*(メモ|めも)[：:]?(<br />)(.+)?(<br />)", str(content))
                tex = memo.group(3)  #記録用の要素取り出し
                #書き出し処理＆保存
                with codecs.open('game\\memo_word.txt', 'a', 'UTF-8') as f:
                    f.write(tex + ">>" + account["acct"] + "\r\n" )
                # bot.rets(5, "メモしました（*'∀'人）", "public")
                return "メモしました（*'∀'人）"
            except:
                # bot.rets(5, "メモに失敗しました(｡>﹏<｡)", "public")
                return "メモに失敗しました(｡>﹏<｡)"
                pass
            pass
        count.memo =+ 1
        # ある程度溜まったらメモまとめをお願いするシステムの予定
        # めそ
        pass

    def poem(status):
        account = status["account"]
        content = Re1.text(status["content"])
        if account["acct"] == "twotwo":
            if re.compile("ﾄｩﾄｩﾄｩﾄｩｰﾄｩ[：:]").search(content):
                poes = re.search("(ﾄｩﾄｩﾄｩ)(ﾄｩｰﾄｩ)[：:]<br />(.*)", str(content))
                Poe = poes.group(3)
                if len(content) > 60:
                    toot_now = "٩(๑`^´๑)۶ﾄｩﾄｩ！！！！！！"
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)
                else:
                    Poe = re.sub("<br />", "\\n", Poe)
                    f = codecs.open('game\\poem_word.txt', 'a', 'UTF-8')
                    f.write(str(Poe) + " &,@" + account["acct"] + "\r\n" )
                    f.close()
                    v = threading.Timer(5, game.fav, [status["id"]])
                    v.start()
            elif re.compile("ﾄｩﾄｩﾄｩﾄｩｰﾄｩﾄｩ!").search(content):
                f = codecs.open('game\\poem_word.txt', 'r', 'utf-8')
                word1 = []
                for x in f:
                    word1.append(x.rstrip("\r\n").replace('\\n', '\n'))
                f.close()
                m = len(word1)
                word2 = []
                for x in range(5):
                    s = random.randint(0, m-1)
                    word2.append((word1[s]).split(' &,@'))
                poe0 = unesc(word2[0])
                poe1 = unesc(word2[1])
                poe2 = unesc(word2[2])
                poe3 = unesc(word2[3])
                poe4 = unesc(word2[4])
                toot_now = poe0[0] + "\n" + poe1[0] + "\n" + poe2[0] + "\n" + poe3[
                    0] + "\n" + poe4[0] + "\n(by:@" + poe0[1] + ":-:@" + poe1[1] + ":-:@" + poe2[
                        1] + ":-:@" + poe3[1] + ":-:@"+poe4[1] + ":)\n#ぽえむげーむ"
                g_vis = "public"
                spo = ":@" + account["acct"] + ":トゥートゥー♪♪"
                bot.rets(6, toot_now, g_vis, None, spo)
        else:
            if re.compile("(ぽえむ|ポエム)(ゲーム|げーむ)[：:]").search(content):
                poes = re.search("(ぽえむ|ポエム)(ゲーム|げーむ)[：:]<br />(.*)", str(content))
                Poe = poes.group(3)
                Poe = unesc(Poe)
                sekuhara = bot.block01(status)
                if sekuhara:
                    toot_now = "٩(๑`^´๑)۶えっちなのはよくない！！！！"
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)
                if len(content) > 60:
                    toot_now = "٩(๑`^´๑)۶長い！！！！！！"
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)
                else:
                    Poe = re.sub("<br />", "\\\\n", Poe)
                    f = codecs.open('game\\poem_word.txt', 'a', 'UTF-8')
                    f.write(str(Poe) + " &,@" + account["acct"] + "\r\n" )
                    f.close()
                    v = threading.Timer(5, game.fav, [status["id"]])
                    v.start()
            elif re.compile("ももな.*(ぽえむ|ポエム)(ゲーム|げーむ).*(ひとつ|おねがい|お願い|１つ|一つ)").search(content):
                if account["acct"] != "JC":
                    f = codecs.open('game\\poem_word.txt', 'r', 'utf-8')
                    word1 = []
                    for x in f:
                        word1.append(x.rstrip("\r\n").replace('\\n', '\n'))
                    f.close()
                    m = len(word1)
                    word2 = []
                    for x in range(5):
                        s = random.randint(0, m-1)
                        word2.append((word1[s]).split(' &,@'))
                    poe0 = word2[0]
                    poe1 = word2[1]
                    poe2 = word2[2]
                    poe3 = word2[3]
                    poe4 = word2[4]
                    toot_now = poe0[0] + "\n" + poe1[0] + "\n" + poe2[0] + "\n" + poe3[
                        0] + "\n" + poe4[0] + "\n(by:@" + poe0[1] + ":-:@" + poe1[1] + ":-:@" + poe2[
                            1] + ":-:@" + poe3[1] + ":-:@"+poe4[1] + ":)\n#ぽえむげーむ"
                    g_vis = "public"
                    spo = ":@" + account["acct"] + ":にぽえむ♪♪"
                    bot.rets(6, toot_now, g_vis, None, spo)

    def senryu(status):
        account = status["account"]
        content = Re1.text(status["content"])
        if account["acct"] == "twotwo":
            if re.compile("ﾄｩｰﾄｩｰﾄｩｰﾄｩ[：:]<br />(.+)<br />(.+)<br />(.+)").search(content):
                poes = re.search("(ﾄｩｰﾄｩｰ)(ﾄhuｩｰﾄｩ)[：:]<br />(.+)<br />(.+)<br />(.+)", str(content))
                sen1 = poes.group(3)
                sen2 = poes.group(4)
                sen3 = poes.group(5)
                if len(sen1) > 6 or len(sen2) > 8 or len(sen3) > 6:
                    pass
                else:
                    f = codecs.open('game\\senryu_word.txt', 'a', 'UTF-8')
                    f.write(unesc(sen1) + ">>>" + unesc(sen2) + ">>>" +
                            unesc(sen3) + ">>>" + account["acct"] + "\r\n" )
                    f.close()
                    v = threading.Timer(5, game.fav, [status["id"]])
                    v.start()
            elif re.compile("ﾄｩﾄｩﾄｩ-ﾄｩｰﾄｩ!").search(content):
                f = codecs.open('game\\senryu_word.txt', 'r', 'utf-8')
                word1 = []
                for x in f:
                    word1.append(x.rstrip("\r\n").replace('\\n', '\n'))
                f.close()
                m = len(word1)
                word2 = []
                for x in range(4):
                    s = random.randint(0, m-1)
                    word2.append((word1[s]).split('>>>'))
                h0 = word2[0]
                h1 = word2[1]
                h2 = word2[2]
                h3 = word2[3]
                toot_now = (h0[0] + "\n" + h1[1] + "\n" + h2[2] +"\n（作者：:@" +
                            h3[3] + ":）\n:@" + account["acct"] +":ﾄｩｰﾄｩﾄｩﾄｩｰﾄｩ❤\n#川柳げーむ")
                g_vis = "public"
                bot.rets(6, toot_now, g_vis)
        else:
            if re.compile("(せんりゅう|川柳)(ゲーム|げーむ)[：:]<br />(.+)<br />(.+)<br />(.+)").search(content):
                poes = re.search("(せんりゅう|川柳)(ゲーム|げーむ)[：:]<br />(.+)<br />(.+)<br />(.+)", str(content))
                sen1 = poes.group(3)
                sen2 = poes.group(4)
                sen3 = poes.group(5)
                sekuhara = bot.block01(status)
                if sekuhara:
                    toot_now = "٩(๑`^´๑)۶えっちなのはよくない！！！！"
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)
                if len(sen1) > 6 or len(sen2) > 8 or len(sen3) > 6:
                    pass
                else:
                    f = codecs.open('game\\senryu_word.txt', 'a', 'UTF-8')
                    f.write(str(sen1) + ">>>" + str(sen2) + ">>>" +
                            str(sen3) + ">>>" + account["acct"] + "\r\n" )
                    f.close()
                    v = threading.Timer(5, game.fav, [status["id"]])
                    v.start()
            elif re.compile("ももな.*(せんりゅう|川柳)(ゲーム|げーむ).*(一句|ひとつ|おねがい|お願い|一つ|１つ)").search(content):
                if account["acct"] != "JC":
                    f = codecs.open('game\\senryu_word.txt', 'r', 'utf-8')
                    word1 = []
                    for x in f:
                        word1.append(x.rstrip("\r\n").replace('\\n', '\n'))
                    f.close()
                    m = len(word1)
                    word2 = []
                    for x in range(4):
                        s = random.randint(0, m-1)
                        word2.append((word1[s]).split('>>>'))
                    h0 = word2[0]
                    h1 = word2[1]
                    h2 = word2[2]
                    h3 = word2[3]
                    toot_now = (h0[0] + "\n" + h1[1] + "\n" + h2[2] + "\n（作者：:@" +
                                h3[3] + ":）\n:@" + account["acct"] +":からのリクエストでした❤\n#川柳げーむ")
                    g_vis = "public"
                    bot.rets(6, toot_now, g_vis)
        pass

    def dice(inp):
        l = []
        n = []
        m = []
        x = 0
        try:
            inp = re.sub("&lt;", "<", str(inp))
            inp = re.sub("&gt;", ">", str(inp))
            com = re.search("(\d+)[dD](\d+)([:<>]*)(\d*)([\+\-\*/\d]*)(.*)(<br />|$)", str(inp))
            print(str(com.group()))
            for v in range(1, 7):
                m.append(com.group(v))
            print(m)
            if int(m[1]) == 0:
                result = "面が0の数字は振れないよ……"
            elif int(m[1]) >= 5000000000000001:
                result = "そんないっぱいの面持ってないよ！！！！"
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

    def honyaku(status):
        #ネイティオ語が分かるようになる装置
        #未定！
        pass

    def callmomona(status):
        #呼ばれた回数を数えるやつ！
        #未定！
        pass

    def throw(status):
        #ぶん投げるボケシステム
        pass


class count():
    CT = time.time()
    end = 0
    sec = 0
    timer_hello = 0
    memo = 0
    n = False
    t = False

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
            gc.collect()

    def emo02(point):
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


def enu():
    threading.enumerate()

def go():
    count.timer_hello = 1

def stop():
    count.timer_hello = 0


if __name__ == '__main__':
    count()
    go()
    bot.timer_toot = False
    m = input("start: ")
    if m is "":
        pass
    else:
        bot.rets(5, "(*ﾟ﹃ﾟ*)……はっ！！！！", "public")
        bot.rets(5, m, "public")
    uuu = threading.Thread(target=bot.t_local)
    lll = threading.Thread(target=bot.t_user)
    fff = threading.Thread(target=count.emo01)
    uuu.start()
    lll.start()
    fff.start()
