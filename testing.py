import requests
import pandas as pd

URL = 'https://battle-cats.fandom.com/wiki/Enemy_Release_Order'
r = requests.get(URL)
df_list = pd.read_html(r.text) # this parses all the tables in webpages to a list
df = df_list[0]
df.head()
df = df['Enemy Release Order Table.1'].tolist()
f = open("grabnamesenemies.txt", "a", encoding="utf-8")
f.write(str(df[3:]))
f.close()