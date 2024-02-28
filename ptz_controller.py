from visca_over_ip import Camera
from inputs import get_gamepad
import math
import threading
import time

ip1 = '192.168.0.81'
ip2 = '192.168.0.82'

class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):

        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()


    def read(self): # return the buttons/triggers that you care about in this methode
        x1 = self.LeftJoystickX
        y1 = self.LeftJoystickY
        x2 = self.RightJoystickX
        y2 = self.RightJoystickY
        b1 = self.LeftBumper
        b2 = self.RightBumper
        t1 = self.LeftTrigger
        t2 = self.RightTrigger
        return {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'b1': b1, 'b2': b2, 't1': t1, 't2': t2}

    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_Z':
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'ABS_RZ':
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'BTN_TL':
                    self.LeftBumper = event.state
                elif event.code == 'BTN_TR':
                    self.RightBumper = event.state
                elif event.code == 'BTN_SOUTH':
                    self.A = event.state
                elif event.code == 'BTN_NORTH':
                    self.Y = event.state #previously switched with X
                elif event.code == 'BTN_WEST':
                    self.X = event.state #previously switched with Y
                elif event.code == 'BTN_EAST':
                    self.B = event.state
                elif event.code == 'BTN_THUMBL':
                    self.LeftThumb = event.state
                elif event.code == 'BTN_THUMBR':
                    self.RightThumb = event.state
                elif event.code == 'BTN_SELECT':
                    self.Back = event.state
                elif event.code == 'BTN_START':
                    self.Start = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY1':
                    self.LeftDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY2':
                    self.RightDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY3':
                    self.UpDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY4':
                    self.DownDPad = event.state




if __name__ == '__main__':
    currentcam = Camera(ip1)
    iscamera2 = False
    cam1active = False
    cam2active = False
    joy = XboxController()
    while True:
        controller = joy.read()
        if controller['x1'] > 0.1 or controller['x1'] < -0.1 or controller['y1'] > 0.1 or controller['y1'] < -0.1 or controller['t1'] > 0.1 or cam1active:
            if controller['x1'] < 0.1 and controller['x1'] > -0.1 and controller['y1'] < 0.1 and controller['y1'] > -0.1 and controller['t1'] < 0.1:
                cam1active = False
            else:
                cam1active = True
            if iscamera2:
                currentcam.close_connection()
                currentcam = Camera(ip1)
                iscamera2 = False
            zoom = max(currentcam.get_zoom_position()/1000,1)
            currentcam.pantilt(int(controller['x1'] * -12 / zoom), int(controller['y1'] * 12 / zoom))
            if controller['b1']:
                currentcam.zoom(int(controller['t1'] * -7))
            else:
                currentcam.zoom(int(controller['t1'] * 7))
        if controller['x2'] > 0.1 or controller['x2'] < -0.1 or controller['y2'] > 0.1 or controller['y2'] < -0.1 or controller['t2'] > 0.1 or cam2active:
            if controller['x2'] < 0.1 and controller['x2'] > -0.1 and controller['y2'] < 0.1 and controller['y2'] > -0.1 and controller['t2'] < 0.1:
                cam2active = False
            else:
                cam2active = True
            if not iscamera2:
                currentcam.close_connection()
                currentcam = Camera(ip2)
                iscamera2 = True
            zoom = max(currentcam.get_zoom_position()/1000,1)
            currentcam.pantilt(int(controller['x2'] * -12 / zoom), int(controller['y2'] * 12 / zoom))
            if controller['b2']:
                currentcam.zoom(int(controller['t2'] * -7))
            else:
                currentcam.zoom(int(controller['t2'] * 7))
