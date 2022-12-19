import csv
files = []
for i in range(0, 800):
    files.append('C:\\Users\\fabri\\Desktop\\old\\Desktop\\battlecats data\\bcjp 12.0.1\\assets\\ImageDataLocal\\' + '{:0>3}'.format(i) + '_e02.maanim')
fullswingsvalues = []
for fls in files:
    section = []
    try:
        with open(fls, "r", encoding="utf-8") as f:
            f.readline()
            f.readline()
            v = f.readline()
            ns = int(v)

            for n in range(0, ns):
                data = f.readline().split(",")

                loop = int(data[2])

                num = int(f.readline())

                mini = 2 ** 32 - 1
                maxi = -(2 ** 32 - 1)

                for m in range(0, num):
                    frame = f.readline().split(",")

                    mini = min(mini, int(frame[0]))
                    maxi = max(maxi, int(frame[0]))

                section.append([maxi - mini, loop, -mini])

        duration = 0

        for s in section:
            if s[1] == -1:
                loop = 1
            else:
                loop = s[1]

            if s[2] >= 0:
                duration = max(duration, s[0] * loop)
            else:
                duration = max(duration, s[0] * loop - s[2])

        animlenght = duration + 1
    except FileNotFoundError:
        animlenght = "form doesn't exists"
    except ValueError:
        animlenght = "placeholder"
    fullswingsvalues.append(animlenght)
en_names = []
with open('C:\\Users\\fabri\\Desktop\\old\\Desktop\\battlecats data\\bcen 11.9\\assets\\resLocal\\Enemyname.tsv', 'r', encoding="utf-8") as en_names_file:
    line = en_names_file.readline()
    #todo fix me
    while line:
        if line[:1] in "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0123456789":
            en_names.append(line)  # ダミー = dummy, basically no name assigned
        else:
            en_names.append(line[:-1])  # ダミー = dummy, basically no name assigned
        line = en_names_file.readline()

jp_names = []
with open('C:\\Users\\fabri\\Desktop\\old\\Desktop\\battlecats data\\bcjp 12.0.1\\assets\\resLocal\\Enemyname.tsv', 'r', encoding="utf-8") as jp_names_file:
    line = jp_names_file.readline()
    while line:
        jp_names.append(line[:-1])
        line = jp_names_file.readline()

enemystats = []
with open('C:\\Users\\fabri\\Desktop\\old\\Desktop\\battlecats data\\bcjp 12.0.1\\assets\\DataLocal\\t_unit.csv','r', encoding="utf-8") as enemystatsfile:
    enemystatsfile.readline()  # first 2 lines are useless
    enemystatsfile.readline()
    line = enemystatsfile.readline()
    while line:
        stats_splitted = line.split(',')
        last_elem = stats_splitted.pop()
        if last_elem.endswith('\n'):
            last_elem = last_elem[:-1]
        stats_splitted.append(last_elem)
        stats_splitted.append(fullswingsvalues.pop(0))
        try:
            stats_splitted.append(en_names.pop(0).strip())
        except IndexError:
            stats_splitted.append('Not yet in EN')
        stats_splitted.append(jp_names.pop(0))
        enemystats.append(stats_splitted)
        line = enemystatsfile.readline()
with open("auto_enemies_generated.tsv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(enemystats)

#todo deal with names that are manually given
