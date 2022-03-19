import sqlite3


class Custom_stages:

    @staticmethod
    def remove_name_by_exact_name(new_name):
        try:
            conn = sqlite3.connect('custom_names_for_stages.db')
            cursor = conn.cursor()
            if cursor.execute('''select count(custom_name) as from custom_names where custom_name = ?''', new_name).fetchone()[0]:
                cursor.execute('''delete from custom_names where custom_name=?;''', new_name)
                conn.commit()
                return True
            else:
                return False
        except Exception as E:
            return E

    @staticmethod
    def add_name(real_stage_id, new_name, who, when):
        try:
            conn = sqlite3.connect('custom_names_for_stages.db')
            cursor = conn.cursor()
            cursor.execute('''insert into custom_names values (?,?,?,?);''', (real_stage_id, new_name, who, when))
            conn.commit()
        except Exception as E:
            return E
        return 'The name was successfully added.'

    @staticmethod
    def does_name_exist(stage_exact_name):
        try:
            conn = sqlite3.connect('custom_names_for_stages.db')
            cursor = conn.cursor()
            if cursor.execute('''select count(custom_name) from custom_names where custom_name = ?''', (stage_exact_name,)).fetchone()[0] > 0:
                return True
            else:
                return False
        except Exception as E:
            return E


    @staticmethod
    def get_all_names():
        try:
            conn = sqlite3.connect('custom_names_for_stages.db')
            cursor = conn.cursor()
            return cursor.execute('''select custom_name from custom_names''').fetchall()

        except Exception as E:
            return E

    @staticmethod
    def custom_name_to_id(stage_exact_name):
        try:
            conn = sqlite3.connect('custom_names_for_stages.db')
            cursor = conn.cursor()
            return cursor.execute('''select stage_id from custom_names where custom_name=?''',(stage_exact_name,)).fetchone()

        except Exception as E:
            return E

    @staticmethod
    def setup_table():
        try:
            conn = sqlite3.connect('custom_names_for_stages.db')
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE if not exists "custom_names" (
    "stage_id"	INTEGER NOT NULL,
    "custom_name"	TEXT NOT NULL,
    "who_gave_name"	TEXT NOT NULL,
    "when_name_given"	TEXT NOT NULL,
    PRIMARY KEY("custom_name")
);''')
            conn.commit()
        except Exception as E:
            return E
