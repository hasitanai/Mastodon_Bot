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
status = mastodon.account(ids)
print(status["username"])
t = mastodon.account_statuses(ids, limit=1)
if not t:
    if status['statuses_count'] > 0:
        print("Out")
    else:
        print("foo?")
else:
    for x in t:
        print(x["id"])