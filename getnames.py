# -*- coding: utf-8 -*-
import pandas as pd
import yaml
data = pd.read_json('jpnames.json', encoding='utf-8')  # change to ennames.json to get the english one
datacolumns = data.index
datalist = data.values.tolist()
allvalues=[data.columns.tolist()] + data.values.tolist()
flatten = ['']*1600
posizione = 0
for i in allvalues[0]:
    indice = 0
    for j in allvalues[1][posizione]:
        flatten[(i-1)*3+indice] = j
        indice += 1
    posizione += 1

for i in flatten:
    print(i)
