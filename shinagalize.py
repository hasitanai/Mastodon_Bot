from janome.tokenizer import Tokenizer
import re

def shinagalize(text):
    lines = Tokenizer().tokenize(text)

    last = len(lines)
    target = lines[last - 1]
    if re.search("名詞,サ変接続", target.part_of_speech):
        return ''.join([x.surface for x in lines[0:last]]) + "しながら"
    target = lines[last - 2]
    if re.search("動詞", target.part_of_speech):
        prefix = ''.join([x.surface for x in lines[0:last-2]])
        if target.infl_type == "一段" or re.search("カ変", target.infl_type):
            return prefix + re.sub("る$", "", target.base_form) + "ながら"
        if re.search("サ変", target.infl_type) :
            return prefix + re.sub("する$", "し", target.base_form) + "ながら"
        m = re.search("五段・(.)行", target.infl_type)
        if m:
            mappings = [
                "アいう", "カきく", "ガぎぐ", "サしす", "タちつ",
                "ナにぬ", "バびぶ", "マみむ", "ラりる"
            ]
            m =  m.group(1)
            for mapping in mappings:
                if mapping[0] == m:
                    return prefix + re.sub(mapping[2] + "$", mapping[1], target.base_form) + "ながら"
    return text + "しながら"
