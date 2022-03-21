import sqlite3

def get_guide_from_id(id):
    try:
        conn = sqlite3.connect('guides.db')
        cursor = conn.cursor()
        guide = cursor.execute('''select * from guides where id = ?''', (id,)).fetchone()
        return guide
    except Exception as E:
        return E

def guides_for_stageid(stage_id):
    try:
        conn = sqlite3.connect('guides.db')
        cursor = conn.cursor()
        guides = cursor.execute('''select guide, id from guides where stageid = ?''', (stage_id,)).fetchall()
        if len(guides) > 0:
            return [True, guides]
        else:
            return [False, no_guide()]
    except Exception as E:
        return [False, E]


def no_guide():
    try:
        conn = sqlite3.connect('guides.db')
        cursor = conn.cursor()
        guides = cursor.execute('''select message from 'no-guides' order by RANDOM() limit 1''').fetchall()
        if len(guides) > 0:
            return guides[0][0]
        else:
            return "Problems with database (no except)."
    except Exception as E:
        print(E)
        return "Problems with database."


def add_guide(stage_id, guide):
    try:
        conn = sqlite3.connect('guides.db')
        cursor = conn.cursor()
        cursor.execute('''insert into guides (stageid, guide) values (?,?);''', (stage_id, guide))
        conn.commit()
        return "Added guide."
    except Exception as E:
        return "Something bad happened."


def remove_guide(guide_id):
    try:
        conn = sqlite3.connect('guides.db')
        cursor = conn.cursor()
        if cursor.execute('''select count(guide) from guides where id = ?''', (guide_id,)).fetchone()[0]:
            cursor.execute('''delete from guides where guide=?;''', (guide_id,))
            conn.commit()
            return "Deleted guide."
        else:
            return "Guide didn't exist."
    except Exception as E:
        return "Something bad happened: "+str(E)
