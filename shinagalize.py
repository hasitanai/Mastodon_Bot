from janome.tokenizer import Tokenizer
import re

def shinagalize(text):
    lines = Tokenizer().tokenize(text+"とマストドン")
    last = len(lines)
    to = lines[last - 2]
    target = lines[last - 3]
    if __name__ == '__main__':
        for x in lines:print(x.surface, x.part_of_speech)
    if re.search("^ももな$", text):
        return "私のことを考えながら"
    elif re.search("名詞,サ変接続", target.part_of_speech):
        return ''.join([x.surface for x in lines[0:-2]]) + "しながら"
    elif re.search("名詞,非自立", target.part_of_speech):
        target = lines[last - 4]
        prefix = ''.join([x.surface for x in lines[0:last - 4]])
        if __name__ == '__main__':
            print("【{}】".format(target.surface),
                  target.part_of_speech, target.infl_type, prefix)
        return do(target, prefix, text)
    else:
        prefix = ''.join([x.surface for x in lines[0:last - 3]])
        if __name__ == '__main__':
            print("【{}】".format(target.surface),
                  target.part_of_speech, target.infl_type, prefix)
        if re.search("並立助詞", to.part_of_speech):
            return do(target, prefix, text)
        elif re.search("接続詞", to.part_of_speech):
            return "意味分かんないけど"
        else:
            a = do(target, prefix, text)
            return a + "？"
    
def do(target, prefix, text):
    if re.search("^動詞", target.part_of_speech):
        if target.infl_type == "一段" or re.search("カ変", target.infl_type):
            return prefix + re.sub("る$", "", target.base_form) + "ながら"
        elif re.search("サ変.+スル", target.infl_type) :
            return prefix + re.sub("する$", "し", target.base_form) + "ながら"
        elif re.search("サ変.+ズル", target.infl_type) :
            return prefix + re.sub("ずる$", "じ", target.base_form) + "ながら"
        else:
            m = re.search("五段・(.)行", target.infl_type)
            if m:
                mappings = [
                    "アいう", "カきく", "ガぎぐ", "サしす", "タちつ",
                    "ナにぬ", "バびぶ", "マみむ", "ラりる", "ワいう"
                ]
                m =  m.group(1)
                for mapping in mappings:
                    if mapping[0] == m:
                        return prefix + re.sub(mapping[2] + "$", mapping[1], target.base_form) + "ながら"
    elif re.search("特殊・タ", target.infl_type):
        return prefix + ("ても" if target.base_form == "た" else "でも")
    elif re.search("特殊・ダ", target.infl_type):
        return prefix + "でも"
    elif re.search("特殊・ナイ", target.infl_type):
        return prefix + "ずに"
    elif re.search("連体化", target.part_of_speech):
        return prefix + "と一緒に"
    else:
        return text + "と一緒に"

def test(text):  # テスト用
    lines = Tokenizer().tokenize(text)
    for x in lines:
        print(x.surface, x.part_of_speech)
