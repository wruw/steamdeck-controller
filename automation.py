import time
import PyATEMMax
import random

sleep = 10
atem = '192.168.1.80'

switcher = PyATEMMax.ATEMMax()
switcher.connect(atem)
switcher.waitForConnection()
while True:
    sleeptime = sleep + (random.random() - 0.5) * sleep
    time.sleep(sleeptime)
    channel = random.randint(1,6)
    switcher.setProgramInputVideoSource(0,channel)


