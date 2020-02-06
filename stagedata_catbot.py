import sqlite3

conn = sqlite3.connect('stages.db')

conn.execute('''CREATE TABLE stage(
            stage_id STRING PRIMARY KEY,
            name STRING NOT NULL
            );''')

conn.execute('''CREATE TABLE enemylines(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         stage_appearance STRING NOT NULL,
         unitcode INT NOT NULL,
         amount INT NOT NULL,
         magnification INT NOT NULL,
         r_first_time INT NOT NULL,
         r_second_time INT NOT NULL,
         base hp INT NOT NULL,
         first_layer INT NOT NULL,
         second_layer INT NOT NULL,
         boss INT NOT NULL,
         timer INT NOT NULL,
         dojo_points INT NOT NULL,
         FOREIGN KEY(stage_appearance) REFERENCES stage(stage_id)
         );''')

conn.execute('''CREATE TABLE optional_data(
                opt_data_id INTEGER PRIMARY KEY,
                data STRING,
                FOREIGN KEY(opt_data_id) REFERENCES stage(stage_id)
                );''')


conn.close()
