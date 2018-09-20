# -*- coding: utf-8 -*-

from mastodon import *
from time import sleep
import threading, re, sys, io
import warnings, traceback
"""
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,
                              encoding=sys.stdout.encoding,
                              errors='backslashreplace',
                              line_buffering=sys.stdout.line_buffering)
warnings.simplefilter("ignore", UnicodeWarning)
"""
url_ins = open("instance.txt").read()

mastodon = Mastodon(
    client_id="cred.txt",
    access_token="auth.txt",
    api_base_url=url_ins)  # インスタンス


class d():
    a = 3
    def _init_(self):
        self.a = 0
        pass
    def b(self):
        a = 2
        def c():
            while e == 1:
                a = 1
                e = 1
            return a
        print(a)
        print(self.a)
        return a

d = d()
print(d.b())
