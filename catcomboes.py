import sqlite3
import nltk as nl
import catunits_catbot
class Comboes:

    @staticmethod
    def name_to_combo(name, catculator):
        try:
            conn = sqlite3.connect('file:catcomboes.db?mode=rw', uri=True)  # open only if exists
            cursor = conn.cursor()
            results = cursor.execute("SELECT DISTINCT combo_name FROM units_in_combo").fetchall()
        except sqlite3.OperationalError:  # database not found
            return "Database for cat comboes not found."

        array = []
        for r in results:
            array.append(r[0])
        search = [str(x).lower() for x in array]
        dss = list(map(lambda x: nl.edit_distance(x, name.lower()), search))
        closest = [i for i, x in enumerate(dss) if x == min(dss)]
        if len(closest) > 1:
            conn.close()
            return "Couldn't discriminate catcombo."
        if min(dss) > 6:  # too many errors
            conn.close()
            return "That combo doesn't exists."
        else:
            results = cursor.execute(
                "select distinct required_id,combo_effect from names_effects join units_in_combo on "
                "names_effects.combo_name = units_in_combo.combo_name where names_effects.combo_name = ?",
                (array[closest[0]],)).fetchall()
            toret = "The catcombo named **" + array[closest[0]] + "** with the effect **" + results[0][
                1] + "** requires the following units; "
            for r in results:
                toret = toret + str(catculator.getnamebycode(r[0])) + ", "
            conn.close()
            return toret[:-2] + "."


    @staticmethod
    def search_by_unit(unit, catculator):  #needs tests
        unit_id = catculator.getUnitCode(unit.lower(), 6)
        if unit_id == "no result":  # too many errors
            return "That unit doesn't exists."
        if unit_id == "name not unique":  # name wasn't unique
            return "Couldn't discriminate the unit."
        if catculator.getrow(unit_id[0]) is None:
            return "Your unitcode was invalid."
        try:
            conn = sqlite3.connect('file:catcomboes.db?mode=rw', uri=True)  # open only if exists
            cursor = conn.cursor()
            results = cursor.execute("select DISTINCT uic.combo_name, combo_effect, uic.required_id from names_effects join units_in_combo on names_effects.combo_name = units_in_combo.combo_name join units_in_combo as uic on uic.combo_name = names_effects.combo_name where units_in_combo.accepted_id = ?",(unit_id[0],)).fetchall()
        except sqlite3.OperationalError:  # database not found
            return "Database for cat comboes not found."
        if len(results) == 0:
            return "**" + catculator.getnamebycode(unit_id[0]) + "** isn't part of any combo."
        answer = "**" + catculator.getnamebycode(unit_id[0]) + "** belongs to the following comboes:"
        lastcombo = None
        for line in results:

            if line[0] != lastcombo:
                lastcombo = line[0]
                answer = answer + "\n**" + line[1] + " (" + line[0] + ")**: "
            answer = answer + str(catculator.getnamebycode(line[2])) + ', '
        return answer.replace(', \n', '.\n')[:-2] + "."
