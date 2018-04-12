import time, re, sys, os, json, random, io, codecs

l = {}
data_dir_path = u"./thank/"
file_list = os.listdir(r'./thank/')
for file_name in file_list:
    root, ext = os.path.splitext(file_name)
    if ext == u'.txt':
        abs_name = data_dir_path + '/' + file_name
        with open(abs_name, 'r') as f:
            x = f.read()
            if x != "":
                l.update({str(root):int(x)})
            else:
                pass
te1 = ""
for k, v in sorted(l.items(), key=lambda x: x[1]):
    te0 = ":@" + str(k) + ": " + str(v)
    print(te0)
    te1 = "{0}\n{1}".format(te0, te1)
with open("ももなランキング.txt", 'w') as f:
    f.write(te1)
