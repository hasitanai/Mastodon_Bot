import MeCab
import re

def shinagalize(text):
    parsed = MeCab.Tagger("-Ochasen").parse(text)
    parsed = re.sub("\nEOS\n", '', parsed)
    lines = [x.split("\t") for x in parsed.split("\n")]
    last = len(lines)
    if re.search("名詞-サ変接続", lines[last - 1][3]):
        return ''.join([x[0] for x in lines[0:last]]) + "しながら"
    elif re.search("動詞", lines[last - 2][3]):
        ttype = lines[last - 2][4]
        prefix = ''.join([x[0] for x in lines[0:last-2]])
        base = lines[last - 2][2]
        if ttype == "一段" or re.search("カ変", ttype):
            return prefix + re.sub("る$", "", base) + "ながら"
        if re.search("サ変", ttype) :
            return prefix + re.sub("する$", "し", base) + "ながら"
        m = re.search("五段・(.)行", ttype)
        if m:
            mappings = [
                "アいう", "カきく", "ガぎぐ", "サしす", "タちつ",
                "ナにぬ", "バびぶ", "マみむ", "ラりる"
            ]
            m =  m.group(1)
            for mapping in mappings:
                if mapping[0] == m:
                    return prefix + re.sub(mapping[2] + "$", mapping[1], base) + "ながら"
    return text + "しながら"
