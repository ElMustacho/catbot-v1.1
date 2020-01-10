import pandas as pd

catstats = pd.read_csv('unitsnextgen.csv', sep=',', encoding='utf-8')
print(catstats.head())
mergednames = pd.read_csv('merged.tsv', sep='\t', encoding='utf-8')
print(mergednames.head())
tof = catstats.set_index('innercounting').join(mergednames.set_index('p'), how="outer")
print(tof.head())
tof.to_csv('I hope this is the final version.tsv', sep='\t')
