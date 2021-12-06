import randomname
import datetime
import time

class LifeCycle: 
    def __init__(self):
        self.first_run = True
        self.name = ""
        self.born_dt = None
        self.born_text = ""
        self.death_text = ""
        self.age = ""
        self.dead = False
    
    def delay(self):
        time.sleep(5)

    def born(self):
        self.dead = False
        self.death_text = ""
        self.age = ""
        self.name = randomname.get_name()
        self.name = self.name.replace("-", " ")
        self.name = self.name.title()
        self.born_dt = datetime.datetime.now()
        self.born_text =  self.name + " Born " + self.born_dt.strftime("%d.%m.%Y At %H:%M:%S")

    def death(self):
        self.dead = True
        self.age = datetime.datetime.now() - self.born_dt
        minutes = divmod(self.age.seconds, 60) 
        self.death_text = "Died " + datetime.datetime.now().strftime("%d.%m.%Y At %H:%M:%S")
        if minutes[0] == 0:
            self.age ="Aged " + str(minutes[1]) + " seconds"
        elif minutes[0] == 1:
            self.age = "Aged " + str(minutes[0]) + " minute " + str(minutes[1]) + " seconds"
        else:
            self.age = "Aged " + str(minutes[0]) + " minutes " + str(minutes[1]) +" seconds"

