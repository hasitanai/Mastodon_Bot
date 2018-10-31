from mastodon import *
import warnings, traceback

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

ids = input(">> ")
a = mastodon.account_search(ids, limit=1)
for x in a:
    if x["acct"] == ids:
        print("Hit! →", "[{}]".format(x["display_name"]), "@{}".format(x["acct"]), "ID:{}".format(x["id"]))
        for y in x:
            if y == "id" or y == "username" or y == "acct" or y == "display_name":
                pass
            else:
                print("{}: {}".format(y, x[y]))
        break
    else:
        print("No...")