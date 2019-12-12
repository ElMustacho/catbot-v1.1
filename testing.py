import os

fpath = 'C:\\Users\\Fabrizio\\Desktop\\catbot-v1\\files-backswing\\ordered-files\\'
maximum = 0
with open(fpath+'362true.maanim', "r", encoding="utf-8") as fp:  # open file, ignore the name
    line = fp.readline()  # get all the lines
    cnt = 1  # need to know which line
    while line:
        if line.count(',') == 3:  # ignore the first lines
            currentvalue = int(line[0:line.find(',')])
            if currentvalue > maximum:
                maximum = currentvalue  # 1st number
        line = fp.readline()
        cnt += 1
print(maximum+1)