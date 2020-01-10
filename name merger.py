import pandas as pd

enf = pd.read_csv('unordered en names + rarity.tsv', sep='\t', encoding='utf-8', names=['ue', 'p', 're'], index_col=False)
jpf = pd.read_csv('unordered jp names + rarity.tsv', sep='\t', encoding='utf-8', names=['uj', 'p', 'rj'], index_col=False)
tof = jpf.set_index('p').join(enf.set_index('p'), how="outer")
print(tof)
tof.to_csv('merged.tsv', sep='\t')
