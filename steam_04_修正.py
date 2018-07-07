from mastodon import *
import re, sys, os, json, random, io, gc, math
import threading, requests, pprint, codecs, asyncio
from time import *
from datetime import timedelta, datetime, timezone
import warnings, traceback
import xlrd, xlsxwriter
from xml.sax.saxutils import unescape as unesc
from shinagalize import shinagalize
from dateutil.tz import tzutc  # 変更予定
from urllib import request

mastodon = None

# Winのプロンプトから起動するならこれ追加ね↓

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

# UST設定
JST = timezone(timedelta(hours=+9), 'JST')


class Re1():  # Content整頓用関数(๑°⌓°๑)
    def __init__(self): pass

    def text(self, text):
        text = re.sub('<br />', '\n', str(text))
        text = re.sub('<p>|</p>|<a.+"tag">|<a.+"_blank">|<a.+mention">|<'
                      'span>|</span>|</a>|<span class="[a-z-]+">', "", text)
        return unesc(text, {"&apos;": "'", '&quot;': '"'})

    def non_bmp_map(self, code=0xfffd):
        return dict.fromkeys(range(0x10000, sys.maxunicode + 1), code)


Re1 = Re1()


class Log():  # toot記録用クラス٩(๑❛ᴗ❛๑)۶
    def __init__(self, status):
        self.account = status["account"]
        self.mentions = status["mentions"]
        self.content = Re1.text(status["content"])
        self.content = unesc(self.content)
        self.non_bmp_map = Re1.non_bmp_map()
        self.visibility = status["visibility"]

    def read(self, lt):
        name = self.account["display_name"]
        acct = self.account["acct"]
        non_bmp_map = self.non_bmp_map
        text = (("===【{}タイムライン】===").format(lt) + "\n" +
                str(name).translate(non_bmp_map) +
                "@" + str(acct).translate(non_bmp_map) + "\n" +
                 str(self.content).translate(non_bmp_map) + "\n" +
                 "【{}】".format(self.visibility) + str(self.mentions).translate(non_bmp_map)
                )
        print(text)

    def write(self):
        global nowing
        text = self.content
        acct = self.account["acct"]
        with codecs.open('log\\' + 'log_' + nowing + '.txt', 'a', 'UTF-8') as f:
            f.write(str(text) + ',<acct="' + acct + '">\r\n')


class bot():
    def _init_(self):
        pass

    def res(self, sec):
        count.end = count.end - sec
        if count.end < 0:
            count.end = 0

    def rets(self, sec, toot_now, g_vis, rep=None, spo=None):
        now = time()
        delay = now - count.CT
        loss = count.end - int(delay)
        if loss < 0:
            loss = 0
        ing = sec + loss
        t = threading.Timer(ing, self.toot, [toot_now, g_vis, rep, spo])
        t.start()
        print("【次までのロスタイム:" + str(count.end + sec) + "】")
        s = threading.Timer(ing, self.res, [sec])
        s.start()
        del t
        del s
        gc.collect()
        count.CT = time()
        count.end = ing

    def toot(self, toot_now, g_vis, rep=None, spo=None):
        mastodon.status_post(status=toot_now,
                             visibility=g_vis,
                             in_reply_to_id=rep,
                             spoiler_text=spo)
        print("【次までのロスタイム:" + str(count.end) + "】")
        """
        visibility これで公開範囲を指定できるよ！: public, unlisted, private, direct
        """

    def standby(self):
        print("「(๑•̀ㅁ•́๑)✧＜tootｽﾃﾝﾊﾞｰｲ」")

    def thank(self, account, point):
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

    def fav_now(self, fav):  # ニコります
        mastodon.status_favourite(fav)
        print("◇Fav")

    def rand_w(self, txt_deta):
        f = codecs.open(txt_deta, 'r', 'utf-8')
        l = []
        for x in f:
            l.append(x.rstrip("\r\n").replace('\\n', '\n'))
        f.close()
        m = len(l)
        s = random.randint(1, m)
        return l[s - 1]

    def emo(self, user):
        data_dir_path = u"./thank/"
        file_list = os.listdir(r'./thank/')
        abs_name = data_dir_path + '/' + user + '.txt'
        with open(abs_name, 'r') as f:
            x = f.read()
        return x

    def load_json(self, folder, name):
        file = ("game\\{0}\\{1}.json").format(folder, name)
        if os.path.exists(file):
            with codecs.open(file, 'r', 'utf-8', "ignore") as f:
                date = json.load(f)
        else:
            date = ""
        return date

    def load_txt(self, folder, name):
        file = ("game\\{0}\\{1}.txt").format(folder, name)
        if os.path.exists(file):
            with codecs.open(file, 'r', 'utf-8', "ignore") as f:
                date = f.read()
        else:
            date = ""
        return date

    def dump_json(self, folder, name, date, mode):
        dir = "game\\{0}".format(folder)
        if not os.path.isdir(dir):
            os.mkdir(dir)
        file = ("game\\{0}\\{1}.json").format(folder, name)
        with codecs.open(file, mode, 'utf-8', "ignore") as f:
            json.dump(date, f)

    def write_txt(self, folder, name, date, mode):
        dir = "game\\{0}".format(folder)
        if not os.path.isdir(dir):
            os.mkdir(dir)
        file = ("game\\{0}\\{1}.txt").format(folder, name)
        with codecs.open(file, mode, 'utf-8', "ignore") as f:
            f.write(date)


class Home(StreamListener, bot):
    def on_update(self, status):
        account = status["account"]
        try:
            HTL(status)
            if status["visibility"] != "public":
                log = threading.Thread(Log(status).read("ホーム"))
                log.run()
            elif re.search("@[a-zA-Z0-9_]+@[a-zA-Z0-9_]+\.[a-zA-Z]+", account["acct"]):
                log = threading.Thread(Log(status).read("ホーム"))
                log.run()
            pass
        except Exception as e:
            if status["visibility"] != "public":
                print("エラー情報【USER】\n" + traceback.format_exc())
                with open('error.log', 'a') as f:
                    traceback.print_exc(file=f)
            elif re.search("@[a-zA-Z0-9_]+@[a-zA-Z0-9_]+\.[a-zA-Z]+", account["acct"]):
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
                men(status)
            elif notification["type"] == "favourite":
                account = notification["account"]
                print(str(account["display_name"]).translate(non_bmp_map) +
                      "@" + str(account["acct"]) + "からニコってくれたよ₍₍ ◝(●˙꒳˙●)◜ ₎₎\n")
                self.thank(account, 32)
            elif notification["type"] == "reblog":
                account = notification["account"]
                print(str(account["display_name"]).translate(non_bmp_map) +
                      "@" + str(account["acct"]) + "がブーストしてくれたよ(๑˃́ꇴ˂̀๑)\n")
                self.thank(account, 32)
            print(" ")
            pass
        except Exception as e:
            print("エラー情報【USER】\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                f.write("【{}】".format("notification"))
                traceback.print_exc(file=f)
            pass


class Local(StreamListener, bot):
    def on_update(self, status):
        try:
            log = threading.Thread(Log(status).read("ローカル"))
            log.run()
            Log(status).write()
            ltl = threading.Thread(LTL(status))
            ltl.run()
            print("   ")
            pass
        except Exception as e:
            print("エラー情報【LOCAL】\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                f.write("【{}】".format(str(status["url"])))
                traceback.print_exc(file=f)
            pass

    def on_delete(self, status_id):
        print(str("===削除されました【{}】===").format(str(status_id)))


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
                bot().rets(4, toot_now, g_vis)
    else:
        res.check03(status)


def LTL(status):  # ここに受け取ったtootに対してどうするか追加してね（*'∀'人）
    # 以下bot機能の一覧
    res.check01(status)
    res.fav01(status)
    res.fav02(status)
    res.res01(status)
    res.res02(status)
    res.res03(status)
    res.res04(status)
    res.res05(status)
    res.check00(status)
    res.check02(status)
    game.poem(status)
    game.senryu(status)
    game.cinema(status)
    game.prof(status)
    game.quest(status)
    game.habit(status)
    game.callmomona(status)
    # ここまで


def men(status):
    account = status["account"]
    mentions = status["mentions"]
    content = unesc(Re1.text(status["content"]))
    non_bmp_map = Re1.non_bmp_map()
    log = threading.Thread(Log(status).read("ホーム"))
    log.run()
    bot().thank(account, 64)
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
            if re.compile("(アラーム|[Aa][Rr][Aa][Mm])(.*)「(.+)」").search(content):
                mes = re.search("「(.*)」", content)
                toot_now = ("@" + account["acct"] + " " + "（*'∀'人）時間だよーー♪♪\n"
                                                          "「" + mes.group(1) + "」")
            else:
                toot_now = "@" + account["acct"] + " " + "（*'∀'人）時間だよーー♪♪"
            g_vis = status["visibility"]
            t = threading.Timer(sec, bot().toot, [toot_now, g_vis, status['id']])
            t.start()
            print("●アラームを設定したよ！")
            # bot.rets(sec, toot_now, g_vis,status['id'] )
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
                name = re.search("対象[：:]([A-Za-z0-9_]+)<br >"
                                 "(point|ぽいんと|ポイント)[：:](\d+)", str(content))
                name = name.group(1)
                point = int(name.group(3))
                ids = status["id"]
                bot.trial(name, point, ids)
                pass
        elif re.compile("ももな(図鑑|ずかん)の?([修訂]正)：.+").search(content):
            com = re.search("ももな(図鑑|ずかん)の?([修訂]正)：(.+)", str(content))
            tx = com.group(2)
            bot.toot("@lamazeP ももな図鑑の訂正要望が来たよ！！\n"
                     ":@{0}: 「{1}」".format(account["acct"], tx), "direct", status["id"])
        else:
            pass
    v = threading.Timer(5, bot.fav_now, [status["id"]])
    v.start()


class res(bot):
    def block01(self, status):
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
                self.toot("@lamazeP (｡>﹏<｡)これってセクハラですか？？\n:@{0}: 「{1}」".format(str(account["acct"]),
                         str(content)), "direct", status["id"])
                self.thank(account, -64)
                break
            else:
                j = False
        return j

    def block02(self, status):
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
                self.toot("@lamazeP (｡>﹏<｡)こちらはですか？？\n:@{0}: 「{1}」".format(str(account["acct"]),
                                                                          str(content)), "direct", status["id"])
                self.thank(account, -64)
                break
            else:
                j = False
        return j

    def trial01(self, name, point, ids):  # デバック用
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
        self.toot(toot_now, "direct", ids)
        pass

    def check00(self, status):
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
                    self.rets(4, toot_now, g_vis)
                elif re.match('^\d000$', str(ct)):
                    toot_now = (" :@" + account['acct'] + ": @" +
                                account['acct'] + "\n（*'∀'人）" + str(ct) +
                                'tootおめでとーー♪')
                    g_vis = "public"
                    self.rets(4, toot_now, g_vis)
        else:
            pass

    def check01(self, status):
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

    def check02(self, status):
        account = status["account"]
        created_at = status['created_at']
        if isinstance(created_at, str):
            with codecs.open('at_time\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:  # 書き込みモードで開く
                f.write(created_at)  # \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z
        elif isinstance(created_at, datetime):
            z = created_at.isoformat()
            y = re.sub("...$", "Z",z)
            with codecs.open('at_time\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:  # 書き込みモードで開く
                f.write(y)  # \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z
        else:
            print("▼書き込めませんでした")

    def check03(self, status):
        account = status["account"]
        ct = account["statuses_count"]
        if account["acct"] == "Knzk":  # 神崎おにいさん監視隊
            ct += 5
            if re.match('^\d+000$', str(ct)):
                toot_now = "@Knzk (๑•̀ㅁ•́๑)神崎おにいさん！！\n" + str(ct) + 'tootまであと5だよ！！！！'
                g_vis = "direct"
                self.rets(4, toot_now, g_vis)
        elif account["acct"] == "5":  # やなちゃん監視隊
            ct += 5
            if re.match('^\d+0000$', str(ct)):
                toot_now = "@5 (๑•̀ㅁ•́๑)やなちゃん！！\n" + str(ct) + 'tootまであと5だよ！！！！'
                g_vis = "direct"
                self.rets(4, toot_now, g_vis)
        elif account["acct"] == "yzhsn":  # 裾野監視隊
            ct += 5
            if re.match('^\d+000$', str(ct)):
                toot_now = "@yzhsn (๑•̀ㅁ•́๑)おい裾野！！\n" + str(ct) + 'tootまであと5だよ！！！！'
                g_vis = "direct"
                self.rets(4, toot_now, g_vis)
        elif account["acct"] == "lamazeP":  # ラマーズＰ監視隊
            ct += 5
            if re.match('^\d+000$', str(ct)):
                toot_now = "@lamazeP (๑•̀ㅁ•́๑)" + str(ct) + 'tootまであと5だよ！！！！'
                g_vis = "direct"
                self.rets(4, toot_now, g_vis)
        else:  # テスト
            ct += 5
            if re.match('^\d+000$', str(ct)):
                toot_now = ("@" + account["acct"] +
                            " (๑•̀ㅁ•́๑)ただいまフォローしてる方にお知らせだよ！\n" + str(ct) +
                            'tootまであと5だよ！！！！')
                g_vis = "direct"
                self.rets(4, toot_now, g_vis)

    def res01(self, status):
        account = status["account"]
        content = re.sub("<p>|</p>", "", str(status['content']))
        path = 'thank\\' + account["acct"] + '.txt'
        xxx = "[(（].+[)）]|@[a-zA-Z0-9_]+|\s|＠.+|:"
        try:
            with codecs.open('date\\adana\\' + account["acct"] + '.txt', 'r', 'UTF-8') as f:
                name = f.read()
            if re.compile("^[ -/　-】:-\?\[-`\{-~]+$").search(name):
                if account['display_name'] == "":
                    name = account['acct']
                else:
                    name = re.sub(xxx, "", account['display_name'])
            elif name == "":
                if account['display_name'] == "":
                    name = account['acct']
                else:
                    name = re.sub(xxx, "", account['display_name'])
        except:
            if account['display_name'] == "":
                name = account['acct']
            else:
                name = re.sub(xxx, "", account['display_name'])
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
                        self.rets(20, toot_now, g_vis)
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
                            self.rets(6, toot_now, "public")
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
                        self.rets(6, toot_now, "public")
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
                        self.rets(6, toot_now, "public")
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
                                    posting = "(｡>﹏<｡)暫く会えなくて寂しかったよーーーー！！！！\n#ニコフレ挨拶部"
                                else:
                                    posting = "（*'∀'人）おひさひさーーーー♪\n#ニコフレ挨拶部"

                                toot_now = (":@{0}: {1}\n{2}".format(account['acct'], name, posting))
                                self.rets(6, toot_now, "public")
                            elif delta.total_seconds() >= 10800:
                                if now_time.hour in range(3, 9):
                                    posting = self.rand_w('time\\kon.txt')
                                elif now_time.hour in range(9, 19):
                                    posting = self.rand_w('time\\kob.txt')
                                else:
                                    posting = self.rand_w('time\\oha.txt')
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
                                self.rets(6, toot_now, "public")

                        except:
                            print("○初あいさつします（*'∀'人）")
                            try:
                                v = threading.Timer(2, mastodon.status_reblog, [status["id"]])
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
                            self.rets(6, toot_now, "public")
                            if shinki is True:
                                self.toot("@lamazeP 新規さんが来たよーー（小声）\n【" + str(account['acct']) + "】",
                                         "direct", status["id"])
                            try:
                                if re.match('^\d+000$', str(ct)):
                                    toot_now = "°˖✧◝(⁰▿⁰)◜✧˖" + str(ct) + 'toot達成ーーーー♪♪'
                                    g_vis = "public"
                                    self.rets(4, toot_now, g_vis)
                            except:
                                print("○キリ番に気づいていないようです")
                                pass
        else:
            print("○反応がない人なので挨拶しません（*'∀'人）")

    def res02(self, status):
        account = status["account"]
        content = Re1.text(status["content"])
        if account["acct"] != "JC":
            matches = re.search("([^>]+)とマストドン[、]?(どちら|どっち)が大[切事]か[分わ]かってない", content)
            if matches:
                print("○hitしました♪")
                sekuhara = self.block01(status)
                bougen = self.block02(status)
                if len(content) > 60:
                    toot_now = "٩(๑`^´๑)۶長い！！！！！！"
                    g_vis = "public"
                    self.rets(5, toot_now, g_vis)
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
                    self.rets(5, toot_now, g_vis)

    def res03(self, status):
        account = status["account"]
        if account['acct'] != "kiri_bot01":
            if account["acct"] != "JC":
                if re.compile("ももな([^\d]*)[1-5][dD]\d+").search(status['content']):
                    print("○hitしました♪")
                    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
                    coro = Re1.text(str(status['content']).translate(non_bmp_map))
                    toot_now = ":@" + account["acct"] + ": @" + account["acct"] + "\n" + game.dice(coro)
                    self.rets(8, toot_now, status["visibility"])
                elif re.compile("ももな(.*)([6-9]|\d{2})[dD](\d*)").search(status['content']):
                    toot_now = "@{} ６回以上の回数は畳む内容だからメンションの方で送ってーー！！".format(account["acct"])
                    self.rets(6, toot_now, status["visibility"], status["id"])

    def res04(self, status):  # あだ名実装
        account = status["account"]
        profile_emojis = status["profile_emojis"]
        if account["acct"] != "JC":
            data_dir_path = u"./thank/"
            abs_name = data_dir_path + '/' + account["acct"] + '.txt'
            with open(abs_name, 'r')as f:
                x = f.read()
                y = int(x)
            if re.compile("ももな.*あだ[名な][｢「](.+)[」｣](って|と)[呼よ]んで").search(status['content']):
                if y >= 0:
                    print("○hitしました♪")
                    ad = re.search("ももな.*あだ[名な][｢「](.+)[」｣](って|と)[呼よ]んで", status['content'])
                    name = ad.group(1)
                    adan = Re1.text(name)
                    adan = re.sub(':', '', adan)
                    adan = re.sub('(@[a-zA-Z0-9_]+)', ':\1:', adan)
                    sekuhara = self.block01(status)
                    bougen = self.block02(status)
                    if len(adan) > 50:
                        toot_now = "٩(๑`^´๑)۶長い！！！！！！"
                    else:
                        if sekuhara:
                            toot_now = "(｡>﹏<｡)そんないやらしい呼び方出来ないよーー……"
                        elif bougen:
                            toot_now = "(｡>﹏<｡)ふぇぇ暴言怖いよーー……"
                        elif re.compile("^[　.。,、 -]+$").search(adan):
                            toot_now = "٩(๑`^´๑)۶ちゃんとあだ名つけて！！！！"
                        else:
                            with codecs.open('date\\adana\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:
                                f.write(adan)
                            toot_now = ("@{1} ٩(๑> ₃ <)۶分かったーーーー！！\n「{0}」って呼ぶようにするね！！" \
                                        "#ももなのあだ名事情".format(adan, account["acct"]))
                    self.rets(6, toot_now, status["visibility"], status["id"])
            elif re.compile("ももな.*:@([A-Za-z0-9_]+): ?(さん)?のこと.*[｢「](.+)[」｣]って[呼よ]んで").search(status['content']):
                ad = re.search("ももな.*:@([A-Za-z0-9_]+): ?のこと.*[｢「](.+)[」｣]って[呼よ]んで", status['content'])
                acct = ad.group(1)
                print("○hitしました♪")
                if y >= 50000 or account["acct"] == "lamazeP":
                    name = ad.group(2)
                    adan = Re1.text(name)
                    adan = re.sub(':', '', adan)
                    adan = re.sub('@[a-zA-Z0-9_]+', '', adan)
                    sekuhara = self.block01(status)
                    bougen = self.block02(status)
                    if acct == account["acct"]:
                        if sekuhara:
                            toot_now = "(｡>﹏<｡)そんないやらしい呼び方出来ないよーー……"
                        elif bougen:
                            toot_now = "(｡>﹏<｡)ふぇぇ暴言怖いよーー……"
                        elif re.compile("^[　.。,、 -]+$").search(adan):
                            toot_now = "٩(๑`^´๑)۶ちゃんとあだ名つけて！！！！"
                        else:
                            with codecs.open('date\\adana\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:
                                f.write(adan)
                            toot_now = ("@{1} ٩(๑> ₃ <)۶分かったーーーー！！\n「{0}」って呼ぶようにするね！！"
                                        "#ももなのあだ名事情".format(adan, account["acct"]))
                    elif len(adan) > 50:
                        toot_now = "٩(๑`^´๑)۶長い！！！！！！"
                    else:
                        try:
                            abs_it = data_dir_path + '/' + acct + '.txt'
                            with open(abs_it, 'r')as f:
                                x = f.read()
                                z = int(x)
                            if not sekuhara:
                                if account["acct"] == "lamazeP":
                                    y = + 1000000000
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
                self.rets(6, toot_now, "public")
            elif re.compile("ももな.*あだ[名な](キャンセル|消して)").search(status['content']):
                print("○hitしました♪")
                with codecs.open('date\\adana\\' + acct + '.txt', 'w', 'UTF-8') as f:
                    f.write("")
                toot_now = ("@{} ٩(๑> ₃ <)۶分かったーーーー！！\n次からは普通に呼びかけるね！！".format(account["acct"]))
                self.rets(6, toot_now, status["visibility"], status["id"])
            elif re.compile("ももな.*:@([A-Za-z0-9_]+): ?のあだ[名な](を?教えて|(って|は)何)").search(status['content']):
                ad = re.search("ももな.*:@([A-Za-z0-9_]+): ?のあだ[名な](を?教えて|(って|は)何)", status['content'])
                acct = ad.group(1)
                print("○hitしました♪")
                try:
                    with codecs.open('date\\adana\\' + acct + '.txt', 'r', 'UTF-8') as f:
                        name = f.read()
                    toot_now = (":@{1}:のあだ名は「{0}」だよ！！！！".format(name, acct))
                except:
                    toot_now = (":@{}:のあだ名は設定してないよ！！！！".format(acct))
                self.rets(6, toot_now, "public")

    def res05(self, status):  # t.co警察とか
        account = status["account"]
        content = Re1.text(status["content"])
        if re.search('^あ$', content):
            if account["acct"] != "JC":
                print("○hitしました♪")
                toot_now = ("い".format(account["acct"]))
                self.rets(1, toot_now, "public")
        elif re.search('^あっ$', content):
            if account["acct"] != "JC":
                print("○hitしました♪")
                toot_now = ("いっ".format(account["acct"]))
                self.rets(1, toot_now, "public")
        elif re.search('(ぬるぽ|NullPointerException)', content):
            if account["acct"] != "JC":
                print("○hitしました♪")
                toot_now = ("ｶﾞｯ".format(account["acct"]))
                self.rets(1, toot_now, "public")
        elif re.search('ちくわ大明神', content):
            if account["acct"] != "JC":
                print("○hitしました♪")
                toot_now = ("(๑•̀ㅁ•́๑)誰だ今の！？".format(account["acct"]))
                self.rets(2, toot_now, "public")
        elif re.search('(?:[^a-z0-9_-]|^)t\.co/[a-zA-Z0-9]', status["content"]):
            if account["acct"] != "JC":
                if count.t == False:
                    print("○hitしました♪")
                    toot_now = ("t.co！？".format(account["acct"]))
                    self.rets(2, toot_now, "public")
                    count.t = True
                    def cool():
                        count.t = False
                    t = threading.Timer(90, cool)
                    t.start()
                else:
                    print("○t.coしつこい٩(๑`^´๑)۶")
                self.thank(account, -32)
        elif re.compile("(なんでも(する|します)|何でも(する|します)|ナンデモ(する|します|シマス)|ナンでも(する|します))").search(content):
            if not account["acct"] != "4_0s":
                if count.n == False:
                    print("○hitしました♪")
                    toot_now = ("ん？".format(account["acct"]))
                    self.rets(2, toot_now, "public")
                    count.n = True
                    def cool():
                        count.n = False
                    t = threading.Timer(180, cool)
                    t.start()

    def fav01(self, status):
        account = status["account"]
        if re.compile("(ももな|:@JC:|ちゃんもも|:nicoru\d*:|\WJC\W|もなな)").search(status['content']):
            self.thank(account, 8)
            v = threading.Timer(5, self.fav_now, [status["id"]])
            v.start()

    def fav02(self, status):  # 期間限定用←とは
        account = status["account"]
        if re.compile("(ラマーズ[PpＰｐ]|[Ll]amaze[Pp])").search(status['content']):
            self.thank(account, 120)
            v = threading.Timer(5, self.fav_now, [status["id"]])
            v.start()
        elif re.compile("(ラマーズ|[Ll]amaze)(さん|くん|ちゃん|君)").search(status['content']):
            self.thank(account, 6)
            v = threading.Timer(5, self.fav_now, [status["id"]])
            v.start()
        elif re.compile("[らラ][まマ]([ＰｐpP]|[ぴピ][いぃー～]|[たさ]ん|ちゃん)").search(status['content']):
            self.thank(account, -240)
        elif re.compile("[pPｐＰ]名?は略さずに呼(ぶべき|ぼう|んで)").search(status['content']):
            self.thank(account, 2400)
            v = threading.Timer(5, self.fav_now, [status["id"]])
            v.start()


class game(bot):
    def prof(self, status):
        account = status["account"]
        content = Re1.text(status["content"])
        profile_emojis = status["profile_emojis"]
        if account["acct"] != "JC":
            spo = None
            if re.compile("ももな.*:@([A-Za-z0-9_]+): ?(さん)?(は|って)こんな(人|ひと|やつ|奴|方).*[：:]").search(content):
                print("○hitしました♪")
                word = re.search("ももな.*:@([A-Za-z0-9_]+): ?(さん)?(は|って)こんな(人|ひと|やつ|奴|方).*[：:](<br />)?(.+)",
                                 str(content))
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
                            with codecs.open("game\\prof\\{}.txt".format(acct), "r", 'utf-8', "ignore") as f:
                                tex0 = f.read()
                            with codecs.open("game\\prof\\{}.txt".format(acct), "r", 'utf-8', "ignore") as f:
                                tex0s = f.readlines()
                            tex3 = ""
                            for x in tex0s:
                                print(x)
                                if re.search(account["acct"], x):
                                    print(x)
                                    over = True
                                else:
                                    tex3 = tex3 + x
                            try:
                                with codecs.open("game\\prof\\{}.txt".format(acct), "w", 'utf-8', "ignore") as f:
                                    print(tex3)
                                    f.write(tex3)
                                print("○上書きしたよ！！！！")
                            except:
                                with codecs.open("game\\prof\\{}.txt".format(acct), "w", 'utf-8', "ignore") as f:
                                    f.write(tex0)
                                print("○上書きできなかったよ……")
                            if len(tex0) > 400:
                                toot_now = ("これ以上:@{}:のこと覚えられないよ……整頓するからもう少し待ってね(｡>﹏<｡)".format(acct))
                            elif re.search("[^:]?@[A-Za-z0-9_]+[^:]?", tex1):
                                toot_now = ("٩(๑`^´๑)۶リプライのいたずらしちゃダメ！！！！")
                                count.emo03(account["acct"], -64)
                            else:
                                with codecs.open("game\\prof\\{}.txt".format(acct), "a", 'utf-8') as f:
                                    f.write(tex2 + "\n")
                                if over == True:
                                    toot_now = (
                                    ":@{0}:ありがと！！\n:@{1}:のこと、覚え直した！！！！".format(account["acct"], acct) + "\n#ももな図鑑")
                                else:
                                    toot_now = (":@{0}:ありがと！！\n:@{1}:の知ってること、また一つ覚えた！！！！".format(account["acct"],
                                                                                                 acct) + "\n#ももな図鑑")
                        except:
                            print("エラー情報【図鑑】\n" + traceback.format_exc())
                            with codecs.open("game\\prof\\{}.txt".format(acct), "a", 'utf-8') as f:
                                f.write(tex2 + "\n")
                            toot_now = (":@{0}:ありがと！！\n:@{1}:のこと覚えた！！！！".format(account["acct"], acct) + "\n#ももな図鑑")
                else:
                    toot_now = (":@{}:は実在しない人だよ……(｡>﹏<｡)".format(acct) + "\n#ももな図鑑")
                self.rets(6, toot_now, "public")
            elif re.compile("ももな.*:@([A-Za-z0-9_]+): ?(さん)?((について|の(こと|事))(教|おし)[えへ]て|って[誰何])").search(content):
                print("○hitしました♪")
                word = re.search("ももな.*:@([A-Za-z0-9_]+): ?(さん)?((について|の(こと|事))(教|おし)[えへ]て|って[誰何])", str(content))
                acct = word.group(1)
                try:
                    with codecs.open("game\\prof\\{}.txt".format(acct), "r", 'utf-8', "ignore") as f:
                        tex0 = f.read()
                        spo = ":@{}:はこんな人だよ！！".format(acct)
                    try:
                        with codecs.open('date\\adana\\' + acct + '.txt', 'r', 'UTF-8', "ignore") as f:
                            name = f.read()
                            adan = name + "だよ！！"
                    except:
                        adan = "まだないみたいだよ！！"
                    toot_now = (tex0 + "\nあだ名は{}".format(adan) + "\n#ももな図鑑")
                except:
                    toot_now = ("(｡>﹏<｡)ごめんね……:@{}:がどんな人なのか分からないの……".format(acct) + "\n#ももな図鑑")
                if len(toot_now) > 500:
                    toot_now = ("(｡>﹏<｡)ごめんね……:@{}:を紹介しようと思ったけど文字数がオーバーしちゃった……".format(acct) + "\n#ももな図鑑")
                self.rets(6, toot_now, "public", spo=spo)

    def movie(self, status):
        account = status["account"]
        content = Re1.text(status["content"])
        word = "ももな.*(今日の|きょうの|本日の|ランダム)動画(\d+)"
        nicoapi = "http://ext.nicovideo.jp/api/getthumbinfo/"
        list1 = ["sm","nm","so"]  #基本的に使うのはこれ
        list2 = ["am","fz","ut","dm",
                 "ax","ca","cd","cw","fx","ig","na","om","sd","sk","yk","yo","za","zb","ze","nl"]
                # 古い形式
        if re.compile(word).search(content):
            g = re.search(word, content)
            try:
                idmax = g.group(2)
                if int(idmax) == 0:
                    pass
                else:
                    num = random.randint(1, int(idmax))
                    for tag in list1:
                        req = request.Request(nicoapi + tag + num)
                        with request.urlopen(req) as response:
                            XmlData = response.read()
                        import xml.etree.ElementTree as ET
                        root = ET.fromstring(XmlData)
                        if root.attrib["status"] == "ok":
                            ok = True
                            break
                        else:
                            ok = False
                    if ok:
                        toot_now = ("見つけた！！！！\n" +
                                    root[0][1].text + "\n" +
                                    root[0][0].text + "\n" +
                                    "投稿者は「{}:{}」だよ！！".format(root[0][19].text,root[0][18].text) +
                                    "\n#ももな動画チャレンジ")
                    else:
                        toot_now = ("「{}」の動画番号は削除されてるみたい(｡>﹏<｡)\n#ももな動画チャレンジ".format(
                            str(num)))
                g_vis = "public"
                self.rets(6, toot_now, g_vis)
            except:
                pass


    def cinema(self, status):
        account = status["account"]
        content = Re1.text(status["content"])
        gameIn = ("(劇場|げきじょう|[Cc]inema|シネマ)(ゲーム|げーむ)[：:]" +
                  "\n【(.+)】\n起[：:](.+)\n承[：:](.+)\n転[：:](.+)\n結[：:](.+)")
        gameOut = "(劇場|げきじょう|[Cc]inema|シネマ)(ゲーム|げーむ)" + ".*(ひとつ|おねが[いひ]|お願[いひ]|[1１一]つ)"
        if re.compile(gameIn).search(content):
            print("○hitしました♪")
            word = re.search(gameIn + "(\n.*)?", str(content))
            sekuhara = self.block01(status)
            if sekuhara:
                self.rets(5, "٩(๑`^´๑)۶えっちなのはよくない！！！！", "public")
            else:
                Title = word.group(3)
                Ki = word.group(4)
                Sho = word.group(5)
                Ten = word.group(6)
                Kets = word.group(7)
                if len(Ki) > 80 or len(Sho) > 80 or len(Ten) > 80 or len(Kets) > 80 or len(Title) > 60:
                    self.rets(5, "٩(๑`^´๑)۶長い！！！！！！", "public")
                    pass
                else:
                    f = codecs.open('game\\cinema_word.txt', 'a', 'UTF-8')
                    f.write(Title + ">>" + Ki + ">>" + Sho + ">>" + Ten + ">>" + Kets + ">>" + account["acct"] + "\r\n")
                    f.close()
                    v = threading.Timer(5, game.fav, [status["id"]])
                    v.start()
                    print("◆　成功しました(∩´∀｀)∩　◆")
            return
        elif re.compile("ももな.*" + gameOut).search(content):
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
                    s = random.randint(0, m - 1)
                    word2.append((word1[s]).split('>>'))
                c0 = word2[0]
                c1 = word2[1]
                c2 = word2[2]
                c3 = word2[3]
                c4 = word2[4]
                c5 = [c0[5], c1[5], c2[5], c3[5], c4[5]]
                cast = list(set(c5[1:]))
                toot_now = ("【タイトル】\n" + unesc(c0[0]) + "\n\n【あらすじ】\n" + unesc(c1[1]) +
                            "\n" + unesc(c2[2]) + "\n" + unesc(c3[3]) + "\n" + unesc(c4[4]) + "\n\n"
                                                                                              "【スタッフ】\n監督：:@" + c0[
                                5] + ":\n主演キャスト：:@" + str("::@".join(cast))) + ":\n#劇場げーむ"
                spo = ":@" + account["acct"] + ":さんに上映開始のお知らせ"
                return self.rets(6, toot_now, "public", None, spo)

    def world(self, status):  # 使われない機能……
        account = status["account"]
        content = Re1.text(status["content"])
        hitting = 'セカイが(.+)になっちゃ(っ[たて]|いま[すし])'
        if re.compile(hitting).search(content):
            wrd = re.search(hitting, str(content))
            toot_now = 'セカイが' + wrd(1) + 'になっちゃった♪'
            self.rets(5, toot_now, "public")
        else:
            pass

    def quest(self, status):  # 連想ゲームをボツにして変わりの予定
        account = status["account"]
        content = Re1.text(status["content"])
        profile_emojis = status["profile_emojis"]
        if account["acct"] != "JC":
            if re.compile("ももな.*:@([A-Za-z0-9_]+): ?の戦闘力を?(教[へえ][てろ]|おし[へえ][てろ]|おねが[ひい]|お願[ひい]|表示)").search(content):
                word = re.search("ももな.*:@([A-Za-z0-9_]+): ?の戦闘力を?(教[へえ][てろ]|おし[へえ][てろ]|おねが[ひい]|お願[ひい]|表示)",
                                 str(content))
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
                        for x in range(1, 101):
                            e = int(pow(x - 1, p) * p) + (10 * x)
                            if e < ex:
                                pass
                            else:
                                xx = e - ex
                                lv = x
                                break
                        ak = int(it["followers_count"] / 3) + int(lv * it["followers_count"] / 400) + lv
                        df = int(it["following_count"] / 3) + int(lv * it["followers_count"] / 400) + lv
                        hp = int(((df / 60) + lv) * (int(ex / 1000) + 1))
                        mn = int(min(it["followers_count"], it["following_count"]))
                        mx = int(max(it["followers_count"], it["following_count"]))
                        mp = int(max(mn - ((mx - mn) / 8), 0))
                        try:
                            g = int(game.emo(it["acct"]))
                            if g < 0:
                                g = 0
                            a = datetime.strptime(re.sub("Z", "", status['created_at']), '%Y-%m-%dT%H:%M:%S.%f')
                            a = a.replace(tzinfo=tzutc())
                            b = it['created_at']
                            d = a - b
                            ra = int(math.sqrt(d.days / ex) * 10) + int(it["followers_count"] / 1000)
                            if ra >= 20:
                                ra = "20(MAX)"
                            toot_now = (":@{0}:の戦闘力だよ！！\nLv：{1}　レア度：{2}\n"
                                        "攻撃力：{3}\n防御力：{4}\n"  # "かしこさ：{9}\nみりょく：{10}\n"
                                        "HP：{5}　MP：{6}\n所持金：{7}\n次のLvまで{8}tootだよ！！").format(
                                acct, lv, ra, ak, df, hp, mp, g, xx)
                            toot_now = toot_now + "\n#ももなクエスト"
                        except FileNotFoundError:
                            toot_now = "まだ会ったことがない人だからわからないの(｡>﹏<｡)"
                else:
                    toot_now = '¿?(๑ºㅅº๑)¿?この世に存在しない人だよ！！！！'
                    pass
                self.rets(5, toot_now, "public")
        pass

    def count(self, user):
        i = 0
        f = 0
        b = 0
        u = mastodon.account(user)
        print(u['username'])
        c = mastodon.account_statuses(user, limit=25)
        for x in range(3):
            d = mastodon.account_statuses(user, max_id=(c[-1])["id"], limit=25)
            for x in d:
                c.append(x)
        for x in c:
            f = f + x['favourites_count']
            b = b + x['reblogs_count']
            i = i + 1
            print(x["id"], x['favourites_count'], x['reblogs_count'])

        print(f)
        print(b)
        f = f / i
        b = b / i
        s = {'fav率': f, 'reb率': b}
        print("拾った回数：{}".format(i))
        return s

    def quiz(self, status):  #滞ってる機能
        account = status["account"]
        content = Re1.text(status["content"])
        if re.compile("クイズ(問題|もんだい)[：:]<br />").search(content):
            try:
                qz = re.search("クイズ(問題|もんだい)[：:]<br />[QqＱｑ][.．](.+)<br />"
                               "[AaＡａ][.．](.+)", str(content))
                # ファイル読み書きモードで呼び出し
                try:
                    with open("game\\quiz.json", "r") as f:
                        quiz = json.load(f)
                except:
                    quiz = {}
                # lenを確認して番号振り
                ("{0}{1}: {2}").format(account["acct"], qz.group(2) + ">>>" + qz.group)
                # 書き出し処理＆保存
                with open("game\\quiz.json", "w") as f:
                    json.dump(quiz, f)
                return ("クイズ問題、登録しました（*'∀'人）\n"
                        "問題番号" + "xxx")
            except:
                return "クイズ問題、登録に失敗しました(｡>﹏<｡)"
                pass
            pass
        elif re.compile("クイズ(回答|解答|かいとう)[：:]<br />").search(content):
            ans = re.search("クイズ(回答|解答|かいとう)[：:]<br />[QqＱｑ][.．](.+)<br />"
                            "[AaＡａ][.．](.+)", str(content))
            pass

    def memo(self, status):
        account = status["account"]
        content = Re1.text(status["content"])
        if re.compile("ももな.*(メモ|めも)[：:]").search(content):
            try:
                memo = re.search("ももな.*(メモ|めも)[：:]?(<br />)(.+)?(<br />)", str(content))
                tex = memo.group(3)  # 記録用の要素取り出し
                # 書き出し処理＆保存
                with codecs.open('game\\memo_word.txt', 'a', 'UTF-8') as f:
                    f.write(tex + ">>" + account["acct"] + "\r\n")
                # self.rets(5, "メモしました（*'∀'人）", "public")
                return "メモしました（*'∀'人）"
            except:
                # self.rets(5, "メモに失敗しました(｡>﹏<｡)", "public")
                return "メモに失敗しました(｡>﹏<｡)"
                pass
            pass
        count.memo = + 1
        # ある程度溜まったらメモまとめをお願いするシステムの予定
        pass

    def poem(self, status):
        account = status["account"]
        content = Re1.text(status["content"])
        if account["acct"] == "twotwo":
            if re.compile("ﾄｩﾄｩﾄｩﾄｩｰﾄｩ[：:]").search(content):
                poes = re.search("(ﾄｩﾄｩﾄｩ)(ﾄｩｰﾄｩ)[：:]<br />(.*)", str(content))
                Poe = poes.group(3)
                if len(content) > 60:
                    toot_now = "٩(๑`^´๑)۶ﾄｩﾄｩ！！！！！！"
                    g_vis = "public"
                    self.rets(5, toot_now, g_vis)
                else:
                    Poe = re.sub("<br />", "\\n", Poe)
                    f = codecs.open('game\\poem_word.txt', 'a', 'UTF-8')
                    f.write(str(Poe) + " &,@" + account["acct"] + "\r\n")
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
                    s = random.randint(0, m - 1)
                    word2.append((word1[s]).split(' &,@'))
                poe0 = unesc(word2[0])
                poe1 = unesc(word2[1])
                poe2 = unesc(word2[2])
                poe3 = unesc(word2[3])
                poe4 = unesc(word2[4])
                toot_now = poe0[0] + "\n" + poe1[0] + "\n" + poe2[0] + "\n" + poe3[
                    0] + "\n" + poe4[0] + "\n(by:@" + poe0[1] + ":-:@" + poe1[1] + ":-:@" + poe2[
                               1] + ":-:@" + poe3[1] + ":-:@" + poe4[1] + ":)\n#ぽえむげーむ"
                g_vis = "public"
                spo = ":@" + account["acct"] + ":トゥートゥー♪♪"
                self.rets(6, toot_now, g_vis, None, spo)
        else:
            if re.compile("(ぽえむ|ポエム)(ゲーム|げーむ)[：:]").search(content):
                poes = re.search("(ぽえむ|ポエム)(ゲーム|げーむ)[：:]<br />(.*)", str(content))
                Poe = poes.group(3)
                Poe = unesc(Poe)
                sekuhara = self.block01(status)
                if sekuhara:
                    toot_now = "٩(๑`^´๑)۶えっちなのはよくない！！！！"
                    g_vis = "public"
                    self.rets(5, toot_now, g_vis)
                if len(content) > 60:
                    toot_now = "٩(๑`^´๑)۶長い！！！！！！"
                    g_vis = "public"
                    self.rets(5, toot_now, g_vis)
                else:
                    Poe = re.sub("<br />", "\\\\n", Poe)
                    f = codecs.open('game\\poem_word.txt', 'a', 'UTF-8')
                    f.write(str(Poe) + " &,@" + account["acct"] + "\r\n")
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
                        s = random.randint(0, m - 1)
                        word2.append((word1[s]).split(' &,@'))
                    poe0 = word2[0]
                    poe1 = word2[1]
                    poe2 = word2[2]
                    poe3 = word2[3]
                    poe4 = word2[4]
                    toot_now = poe0[0] + "\n" + poe1[0] + "\n" + poe2[0] + "\n" + poe3[
                        0] + "\n" + poe4[0] + "\n(by:@" + poe0[1] + ":-:@" + poe1[1] + ":-:@" + poe2[
                                   1] + ":-:@" + poe3[1] + ":-:@" + poe4[1] + ":)\n#ぽえむげーむ"
                    g_vis = "public"
                    spo = ":@" + account["acct"] + ":にぽえむ♪♪"
                    self.rets(6, toot_now, g_vis, None, spo)

    def senryu(self, status):
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
                            unesc(sen3) + ">>>" + account["acct"] + "\r\n")
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
                    s = random.randint(0, m - 1)
                    word2.append((word1[s]).split('>>>'))
                h0 = word2[0]
                h1 = word2[1]
                h2 = word2[2]
                h3 = word2[3]
                toot_now = (h0[0] + "\n" + h1[1] + "\n" + h2[2] + "\n（作者：:@" +
                            h3[3] + ":）\n:@" + account["acct"] + ":ﾄｩｰﾄｩﾄｩﾄｩｰﾄｩ❤\n#川柳げーむ")
                g_vis = "public"
                self.rets(6, toot_now, g_vis)
        else:
            if re.compile("(せんりゅう|川柳)(ゲーム|げーむ)[：:]<br />(.+)<br />(.+)<br />(.+)").search(content):
                poes = re.search("(せんりゅう|川柳)(ゲーム|げーむ)[：:]<br />(.+)<br />(.+)<br />(.+)", str(content))
                sen1 = poes.group(3)
                sen2 = poes.group(4)
                sen3 = poes.group(5)
                sekuhara = self.block01(status)
                if sekuhara:
                    toot_now = "٩(๑`^´๑)۶えっちなのはよくない！！！！"
                    g_vis = "public"
                    self.rets(5, toot_now, g_vis)
                if len(sen1) > 6 or len(sen2) > 8 or len(sen3) > 6:
                    pass
                else:
                    f = codecs.open('game\\senryu_word.txt', 'a', 'UTF-8')
                    f.write(str(sen1) + ">>>" + str(sen2) + ">>>" +
                            str(sen3) + ">>>" + account["acct"] + "\r\n")
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
                        s = random.randint(0, m - 1)
                        word2.append((word1[s]).split('>>>'))
                    h0 = word2[0]
                    h1 = word2[1]
                    h2 = word2[2]
                    h3 = word2[3]
                    toot_now = (h0[0] + "\n" + h1[1] + "\n" + h2[2] + "\n（作者：:@" +
                                h3[3] + ":）\n:@" + account["acct"] + ":からのリクエストでした❤\n#川柳げーむ")
                    g_vis = "public"
                    self.rets(6, toot_now, g_vis)
        pass

    def dice(self, inp):
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

    def habit(self, status):
        account = status["account"]
        content = Re1.text(status["content"])
        acct = account["acct"]
        created_at = status['created_at']
        def ck(name, ct=0):
            today = datetime.now().strftime("%Y-%m-%d")
            load = self.load_json
            dump = self.dump_json
            date = load("habit", acct)
            try:
                if date[name]:
                    if date[name][today]:
                        a = date[name][today]
                    else:
                        a = 0
                else:
                    date.update({name: 0})
            except:
                a = 0
                if not date:
                    date = {}
                    date.update({name: 0})
            a = a + 1
            date[name].update({today: a})
            dump("habit", acct, date, "w")
            try:
                if isinstance(ct,int):
                    ct = ct + 1
                else:
                    ct = 0
            except:
                pass
            return ct
        toot_now = None
        if re.search('[待ま]って$|[待ま]て$|^[待ま]って|^[待ま]て|(いや|ちょっと)([待ま]って)|'
                     '[待ま]て(や|よ|[待ま]て)|[待ま]った)', content):
            print("◆待たない！！！！")
            count.wait = ck("wait", count.wait)
            lx = random.randint(0, 15)
            def text(lx):
                if lx < 4:
                    text=("(๑•̀ㅁ•́๑)いや待てない！！")
                elif lx < 8:
                    text = ("(๑•̀ㅁ•́๑)待てない！！")
                elif lx < 12:
                    text = ("(๑•̀ㅁ•́๑)待ちません！！")
                elif lx < 13:
                    text = ("(๑•̀ㅁ•́๑)時間は待ってはくれないよ！！")
                elif lx < 14:
                    text = ("(๑•̀ㅁ•́๑)その待ったは無効でーーーーす！！")
                else:
                    text = ("(๑•̀ㅁ•́๑)待った警察だ！！")
                return text
            toot_now = text(lx)
            self.rets(5, toot_now, "public")

        if re.search('とり(あえず|ま)', content):
            print("◆とりあえず警察だ！！！！")
            count.tori = ck("tori", count.tori)
            lx = random.randint(0,100)
            if lx >= 50:
                if toot_now is None:
                    if count.tori != 0:
                        toot_now = ("青鶏の味噌和え{}丁！".format(str(count.tori)))
                    else:
                        toot_now = ("青鶏の味噌和え……和え……\n"
                                    "٩(๑`^´๑)۶ああもう！！！！"
                                    "回数忘れたやり直し！！！！".format(str(count.tori)))
                    self.rets(5, toot_now, "public")
                    print("鶏から！")

        if re.search('お[おぉー～]あ[ー～]ひょ[おぉー～]', content):
            print("◆おあひょう文化だ！！！！")
            count.oahyo = ck("oahyo", count.oahyo)
        if re.search('死ね|死んで|^しね$|ﾀﾋね|氏ね$', content):
            if not re.search('死ねる|死ねない|死んで(ほしく|欲しく)ない', content):
                print("◆怖いよ！！！！")
                count.shine = ck("shine", count.shine)
                self.thank(account, -80)
        if re.search('しまった', content):
            print("◆あらら？")
            count.shimatta = ck("shimatta", count.shimatta)

    def honyaku(self, status):
        # ネイティオ語が分かるようになる装置
        # きりぼっとが代用してくれてるので中止
        pass

    def callmomona(self, status):
        # 呼ばれた回数を数えるやつ！
        account = status["account"]
        content = Re1.text(status["content"])
        acct = account["acct"]
        created_at = status['created_at']
        if re.search('ももな', content):
            print("◆呼ばれた気がした！！！！")
            today = datetime.strptime(re.sub("T..:..:..\....Z", "", created_at), '%Y-%m-%d')
            load = game.load_json
            dump = game.dump_json
            date = load("callmomona", acct)
            if date != "":
                try:
                    a = date[today]
                except:
                    a = 0
            else:
                a = 0
            a = a + 1
            date.update({today: a})
            dump("callmomona", acct, date, "w")
            count.tori = count.tori + 1
            lx = random.randint(0,100)
            if lx >= 90:
                toot_now = ("呼んだーーーー？？")
                self.rets(5, toot_now, "public")

    def throw(self, status):
        # ぶん投げるボケシステム
        pass


class clock(bot):
    def __init__(self, wait=0.000001):
        self.sleep = wait
        self.cooltime = False

    def clock(self):
        while 1:
            self.now = datetime.now(JST)
            #  self.timelog(self.now)
            self.prof()

    def timelog(self, time):
        sys.stdout.write("\rroading... {}".format(str(time)))
        sys.stdout.flush()
        sleep(self.sleep)

    def prof(self):
        sleep(self.sleep)
        if self.now.minute == 4 or self.now.minute == 24 or self.now.minute == 44:
            if self.cooltime == False:
                self.cooltime = True
                ls = os.listdir("game/prof/")
                x = len(ls)
                y = random.randint(1, x)
                z = ls[y-1]
                name, ext = os.path.splitext(z)
                tex0 = self.load_txt("prof", name)
                spo = "【定期】:@{}:を紹介するよ！！".format(name)
                try:
                    with codecs.open('date\\adana\\' + name + '.txt', 'r', 'UTF-8', "ignore") as f:
                        name = f.read()
                        adan = name + "だよ！！"
                except:
                    adan = "まだないみたいだよ！！"
                toot_now = (tex0 + "\nあだ名は{}".format(adan) +
                            "\n"
                            "もっとみんなのことを知りたいな……💞\n"
                            "詳しくは固定トゥートで！！\n"
                            "#ももな図鑑")
                if len(toot_now) > 500:
                    toot_now = (tex0 + "\nあだ名は{}".format(adan) +
                            "#ももな図鑑")
                self.rets(10, toot_now, "public", spo=spo)
                def cool():
                    self.cooltime = False
                    print("クールタイム終了！！")
                q = threading.Timer(120, cool)
                q.start()


class count():
    CT = time()
    end = 0
    sec = 0
    timer_hello = 0
    memo = 0
    n = False
    t = False
    tori = 0
    wait = 0
    oahyo = 0
    shine = 0

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


class ready():
    def __init__(self): pass

    def go(self):
        count.timer_hello = 1

    def stop(self):
        count.timer_hello = 0

    def user(self):
        try:
            listener = Home()
            mastodon.user_stream(listener)
        except:
            print("例外情報\n" + traceback.format_exc())
            with open('except.log', 'a') as f:
                f.write("\n\n【" + str(datetime.now) + "】\n")
                traceback.print_exc(file=f)
            sleep(180)
            self.user()
            pass

    def local(self):
        try:
            listener = Local()
            mastodon.local_stream(listener)
        except:
            print("例外情報\n" + traceback.format_exc())
            with open('except.log', 'a') as f:
                f.write("\n\n【" + str(datetime.now) + "】\n")
                traceback.print_exc(file=f)
            sleep(180)
            self.local()
            pass


res = res()
game = game()


if __name__ == '__main__':
    # Logに書き込むファイルを作ります(✿´ ꒳ ` )
    nowing = str(datetime.now(JST).strftime("%Y%m%d%H%M%S"))
    with open('log\\' + 'log_' + nowing + '.txt', 'w') as f:
        f.write("【log_{}】".format(str(datetime.now)) + '\n')
    ready = ready()
    count(), ready.go()  # 設定が入ってるクラスを展開(๑>◡<๑)
    m = input("start: ")
    if m is "":
        pass
    else:
        bot().rets(5, "(*ﾟ﹃ﾟ*)……はっ！！！！", "public")
        bot().rets(5, m, "public")
    uuu = threading.Thread(target=ready.local)
    lll = threading.Thread(target=ready.user)
    fff = threading.Thread(target=count.emo01)
    ccc = threading.Thread(target=clock().clock)
    uuu.start()
    lll.start()
    fff.start()
    ccc.start()