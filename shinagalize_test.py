#!/usr/bin/env python

import unittest
from shinagalize import shinagalize

class ShinagalizeTest(unittest.TestCase):
    def test_n(self):
        self.assertEqual(shinagalize("ももなとセックス"), "ももなとセックスしながら")
    def test_ippan(self):
        self.assertEqual(shinagalize("ももなの処女を食べるの"), "ももなの処女を食べながら")
    def test_gogyo(self):
        self.assertEqual(shinagalize("ももなのおっぱい揉むの"), "ももなのおっぱい揉みながら")
        self.assertEqual(shinagalize("ももなとやるの"), "ももなとやりながら")
        self.assertEqual(shinagalize("ももなのあそこにはめるの"), "ももなのあそこにはめながら")
    def test_sahen(self):
        self.assertEqual(shinagalize("ももなとセックスするの"), "ももなとセックスしながら")
    def test_kahen(self):
        self.assertEqual(shinagalize("ももなの初潮が来るの"), "ももなの初潮が来ながら")
    def test_kami(self):
        self.assertEqual(shinagalize("ももなのおしっこを浴びるの"), "ももなのおしっこを浴びながら")
    def test_shimo(self):
        self.assertEqual(shinagalize("ももなと寝るの"), "ももなと寝ながら")
    def test_sase(self):
        self.assertEqual(shinagalize("ももなにしゃぶらせるの"), "ももなにしゃぶらせながら")

if __name__ == '__main__':
    unittest.main()
