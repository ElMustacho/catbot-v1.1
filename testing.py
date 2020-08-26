import sqlite3

try:
    conn = sqlite3.connect('file:custom_commands.db?mode=rw', uri=True)
    cursor = conn.cursor()
    c = ('!guide if',)
    results = cursor.execute("SELECT answer FROM commands WHERE command = ?", c).fetchone()
    if results is None:
        print(':(')
    else:
        print(results[0])
except(sqlite3.OperationalError):
    print('oh no I failed')