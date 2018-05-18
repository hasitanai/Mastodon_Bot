from mastodon import *
import re, sys, os, json, random, io, gc, math
import threading, requests, pprint, codecs
from time import *
from datetime import timedelta, datetime, timezone
from datetime import time as times
import warnings, traceback
import xlrd, xlsxwriter
from xml.sax.saxutils import unescape as unesc
import asyncio
from shinagalize import shinagalize
from dateutil.tz import tzutc  # 変更予定

url_ins = open("instance.txt").read()

mastodon = Mastodon(
    client_id="cred.txt",
    access_token="auth.txt",
    api_base_url=url_ins)  # インスタンス

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
        sys.stdout.write("\r{}\n\n".format(text))
        sys.stdout.flush()

    def write(self):
        global nowing
        text = self.content
        acct = self.account["acct"]
        with codecs.open('log\\' + 'log_' + nowing + '.txt', 'a', 'UTF-8') as f:
            f.write(str(text) + ',<acct="' + acct + '">\r\n')


class response_toot(StreamListener):
    def on_update(self, status):
        try:
            log = threading.Thread(Log(status).read("ローカル"))
            log.run()
            ltl = threading.Thread(TL(status))
            ltl.run()
            # print("   ")
            pass
        except Exception as e:
            print("エラー情報【LOCAL】\n" + traceback.format_exc())
            with open('error_test.log', 'a') as f:
                f.write(str(status))
                traceback.print_exc(file=f)
            pass

    def on_notification(self, notification):
        print("===on_notification===")
        if notification["type"] == "favourite":
            pass
        elif notification["type"] == "reblog":
            pass
        pass


def TL(status):
    game.habit(status)


class bot():
    def __init__(self, mastodon):
        self.mastodon = mastodon

    def res(self, sec):
        count.end = count.end - sec
        if count.end < 0:
            count.end = 0

    def rets(self, sec, toot_now, g_vis="public", rep=None, spo=None):
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

    def emo(self, user):
        data_dir_path = u"./thank/"
        file_list = os.listdir(r'./thank/')
        abs_name = data_dir_path + '/' + user + '.txt'
        with open(abs_name, 'r') as f:
            x = f.read()
        return x

    def fav(self, id):
        self.mastodon.status_favourite(id)

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


class game(bot):
    def habit(self, status):
        account = status["account"]
        content = Re1.text(status["content"])
        acct = account["acct"]
        if re.search('お[おぉー～]あ[ー～]ひょ[おぉー～]', content):
            print("◆おあひょう文化だ！！！！")
            today = datetime.now().strftime("%Y-%m-%d")
            load = self.load_json
            dump = self.dump_json
            date = load("habit", acct)
            try:
                if date["oahyo"]:
                    oahyo = date["oahyo"]
                    if oahyo[today]:
                        a = oahyo[today]
                    else:
                        a = 0
                else:
                    date.update({"oahyo": 0})
            except:
                a = 0
                if not date:
                    date = {}
                    date.update({"oahyo": 0})
            a = a + 1
            date["oahyo"].update({today: a})
            dump("habit", acct, date, "w")
            count.oahyo = count.oahyo + 1


class clock(bot):
    def __init__(self, wait=0.000001):
        self.sleep = wait
        self.cooltime = False

    def clock(self):
        while 1:
            self.now = datetime.now(JST)
            self.timelog(self.now)

    def timelog(self, time):
        sys.stdout.write("\rroading... {}".format(str(time)))
        sys.stdout.flush()
        sleep(self.sleep)


class count:
    CT = time()
    end = 0
    sec = 0
    timer_hello = 0
    memo = 0
    n = False
    t = False
    tori = 0
    oahyo = 0


game = game(mastodon)


def local():
    listener = response_toot()
    mastodon.local_stream(listener)


if __name__ == '__main__':
    print("試運転します")
    b = threading.Thread(target=local)
    b.start()
    c = threading.Thread(target=clock().clock)
    c.start()

    # mastodon.user_stream(listener)
