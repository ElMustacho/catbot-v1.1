import csv

class untrust:

    def __init__(self):
        try:
            with open('untrust.csv', 'r', newline='') as file:
                self.data = list(csv.reader(file))
        except OSError:  # file doesn't exist
            open('untrust.csv', 'a').close()
            with open('untrust.csv', 'w', newline='') as file:
                self.data = list(csv.reader(file))
            print('Made a new file for untrusting.')

    def get_data(self):
        return self.data

    def add_entry(self, user, mod, reason, date, level):
        new_entry = [user, mod, reason, date, level]
        with open('untrust.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            self.data.append(new_entry)
            writer.writerows(self.data)
        return("added")

    @staticmethod
    def level_to_time(level):
        if level == 1:
            return 3600
        elif level == 2:
            return 3600*3
        elif level == 3:
            return 3600*8
        elif level == 4:
            return 3600*24
        elif level == 5:
            return 3600*24*7
        elif level == 6:
            return 3600*24*30
        else:
            return 3600*24*365
