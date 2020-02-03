import sqlite3

conn = sqlite3.connect('stages.db')

print("Opened database successfully")

conn.execute('''CREATE TABLE enemylines
         (ID INTEGER PRIMARY KEY AUTOINCREMENT,
         unitcode           INT    NOT NULL,
         amount            INT     NOT NULL,
         magnification            INT     NOT NULL,
         r_first_time            INT     NOT NULL,
         r_second_time            INT     NOT NULL,
         base hp            INT     NOT NULL,
         first_layer            INT     NOT NULL,
         second_layer            INT     NOT NULL,
         boss        INT     NOT NULL,
         timer            INT     NOT NULL);''')

conn.close()
