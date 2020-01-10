import yaml
import pandas as pd
total_units=[]
with open("build_bc-jp.yaml", 'r', encoding='utf8') as stream:
    try:
        res = yaml.safe_load(stream)
        units = res['cats']
        for rarity_score, rarity in units.items():
            for unit_number, unit in rarity.items():
                results = unit.get('name')
                formvalue = 0
                for name in results:
                    finallist = [name]
                    finallist.append((unit_number - 1) * 3 + formvalue)
                    finallist.append(rarity_score)
                    formvalue += 1
                    total_units.append(finallist)
    except yaml.YAMLError as exc:
        print(exc)
df = pd.DataFrame(total_units, columns=['name', 'unitcode', 'rarity'])
df.to_csv('unordered jp names + rarity.tsv', sep='\t', header=False, index=False)
