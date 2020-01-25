

import os
import shutil

path = 'C:\\Users\\Fabrizio\\Desktop\\catbot-v1\\files-backswing\\enemy'

files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        files.append(os.path.join(r, file))
# print(files)
fpath = 'C:\\Users\\Fabrizio\\Desktop\\catbot-v1\\files-backswing\\ordered-files\\'
# for fls in files:
#    form = None
#    if fls[-10] == 'f':
#        form = 'evol'
#    if fls[-10] == 'c':
#        form = 'base'
#    if fls[-10] == 's':
#        form = 'true'
#    destpath = fpath + fls[-14:-11] + form + '.maanim'
#    print(destpath)
#    shutil.move(fls, destpath)
fullswingsvalues = []
for fls in files:
    maximum = 0
    if not fls.endswith('02.maanim'):
        continue
    with open(fls, "r", encoding="utf-8") as fp:  # open file, ignore the name
        line = fp.readline()  # get all the lines
        cnt = 1  # need to know which line
        while line:
            if line.count(',') == 3:  # ignore the first lines
                currentvalue = int(line[0:line.find(',')])
                if currentvalue > maximum:
                    maximum = currentvalue  # 1st number
            line = fp.readline()
            cnt += 1
    print(maximum + 1)

# maximum = 0
# maxpos = 0
# with open(fpath+'362true.maanim', "r", encoding="utf-8") as fp:  # open file, ignore the name
#     line = fp.readline()  # get all the lines
#     cnt = 1  # need to know which line
#     while line:
#         if line.count(',') == 3:  # ignore the first lines
#             currentvalue = int(line[0:line.find(',')])
#             if currentvalue > maximum:
#                 maximum = currentvalue  # 1st number
#         line = fp.readline()
#         cnt += 1
# print(maximum)