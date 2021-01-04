import csv

class thin_ice:

    def __init__(self):
        with open('thin_ice.csv', 'r', newline='') as file:
            self.data = list(csv.reader(file))

    def get_data(self):
        return self.data

    def add_entry(self, user, mod, reason, date):
        for line in self.data:
            if line[0] == user:
                return("not again")
        new_entry = [user, mod, reason, date]
        with open('thin_ice.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            self.data.append(new_entry)
            writer.writerows(self.data)
        return("added")

    def is_on_thin_ice(self, user):
        for line in self.data:
            if int(line[0]) == int(user):
                return line
        return None

    def remove_entry(self, user):
        for line in self.data:
            if line[0] == user:
                self.data.remove(line)
                with open('thin_ice.csv', 'w', newline='') as file:
                    csv.writer(file).writerows(self.data)
                return("Removed :)")
        return("not removed :(")