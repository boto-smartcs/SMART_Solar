import json
from datetime import datetime
now = datetime.now()

class Object:
    def toJSon(self):
        return json.dumps(self, default = lambda obj: obj.__dict__, sort_keys = False, indent = 4)

data = Object()
data.Solar = Object()
data.Solar.D_ID = "Solar1"

data.Solar.PV = Object()
data.Solar.PV.Volt = 12.55
data.Solar.PV.Current = 0.5
data.Solar.PV.Power = 6.27

data.Solar.Battery = Object()
data.Solar.Battery.Volt = 12.55
data.Solar.Battery.Current = 0.5
data.Solar.Battery.Remaning = 65

data.Solar.Load = Object()
data.Solar.Load.Volt = 12.55
data.Solar.Load.Current = 0.5
data.Solar.Load.Power = 65

data.Solar.Status = Object()
data.Solar.Status.ConTroller_Temperature = 35.5
data.Solar.Status.UPTIME = now.strftime("%Y-%m-%d, %H:%M:%S")

#print(data.toJSon())