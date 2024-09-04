
from visca_over_ip import Camera
from inputs import get_gamepad
import math
import threading
import PyATEMMax

import tkinter as tk
import threading
import time
import random
from tkinter import Scale

cameras = [False] * 8
camera_weights = [50] * 8
duration = 5

class CancellationToken:
    def __init__(self):
       self.is_cancelled = False

    def cancel(self):
       self.is_cancelled = True
       
    def reset(self):
       self.is_cancelled = False



ct = CancellationToken()

class ToggleButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._toggled = False  # State of the button (False: "Off", True: "On")
        self.config(command=self.toggle)

    def toggle(self):
        """Toggle the button's state and update its text."""
        self._toggled = not self._toggled
        new_text = "Disable Camera " + self.cget("text")[-1] if self._toggled else "Enable Camera " + self.cget("text")[-1]
        self.config(text=new_text)
        cameras[int(self.cget("text")[-1]) - 1] = self._toggled

class RandomButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._toggled = False  # State of the button (False: "Off", True: "On")
        self.config(command=self.toggle)

    def toggle(self):
        """Toggle the button's state and update its text."""
        self._toggled = not self._toggled
        new_text = "Disable Random Camera" if self._toggled else "Enable Random Camera"
        self.config(text=new_text)
        if self._toggled:
            random_camera_thread.start()
        else:
            ct.cancel()
            
class Slider(tk.Scale):
    def __init__(self, column, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.camera = column
        self.config(command=self.slide)
        self.set(50)

    def slide(self, value):
        camera_weights[self.camera] = value

def create_toggle_button(window, text, row, column):
    """Creates a toggle button with the given text at the specified row and column."""
    button = ToggleButton(window, text=text)
    button.grid(row=row, column=column, padx=5, pady=5)
    
def create_slider(window, row, column):
    """Creates a slider at the specified row and column."""
    slider = Slider(column, window, from_=0, to=100, orient="horizontal")
    slider.grid(row=row, column=column, padx=5, pady=5)

def tk_function():
    # Create the main window
    root = tk.Tk()
    root.title("Camera Automation")

    # Create 8 toggle buttons
    for i in range(8):
        create_slider(root, 1, i)
        text = f"Enable Camera {i + 1}"
        column = i
        create_toggle_button(root, text, 2, column)
    button = RandomButton(root, text="Enable Random Camera")
    button.grid(row=3, column=0, padx=5, pady=5)
    duration_scale = Scale(root, from_=1, to=30, orient="horizontal")
    duration_scale.grid(row=3, column=1, padx=5, pady=5)
    duration_scale.set(5)
    duration_scale.config(command = lambda value: set_duration(value))
    # Start the Tkinter event loop
    root.mainloop()
    
def set_duration(value):
    global duration
    duration = value

def random_camera(ct):
    while True:
        global duration
        print(cameras)
        print(camera_weights)
        options = []
        sleepTime = (int(duration))+(int(duration)/2*(random.random()-0.5))
        print("sleeping for {} seconds".format(sleepTime))
        time.sleep(sleepTime) 
        if ct.is_cancelled:
            global random_camera_thread
            ct.reset()
            random_camera_thread = threading.Thread(target=random_camera, args=(ct,))
            break
        active_cameras = [i for i, camera in enumerate(cameras) if camera]
        if(active_cameras):
            for(camera, weight) in zip(active_cameras, camera_weights):
                options.extend([camera] * int(weight))
            print(random.choice(options)+1)
            switcher.setProgramInputVideoSource(0,random.choice(options)+1)


random_camera_thread = threading.Thread(target=random_camera, args=(ct,))


ip1 = '192.168.1.81'
ip2 = '192.168.1.82'
atem = '192.168.1.8'


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
        c1 = self.UpDPad
        c2 = self.RightDPad
        c3 = self.LeftDPad
        c4 = self.DownDPad
        A = self.A
        return {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'b1': b1, 'b2': b2, 't1': t1, 't2': t2, 'c1': c1, 'c2': c2, 'c3': c3, 'c4': c4, 'A': A}

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
                elif event.code == 'ABS_HAT0X':
                    if event.state == -1:
                        self.LeftDPad = 1
                        self.RightDPad = 0
                    elif event.state == 1:
                        self.RightDPad = 1
                        self.LeftDPad = 0
                    else:
                        self.RightDPad = 0
                        self.LeftDPad = 0
                elif event.code == 'ABS_HAT0Y':
                    if event.state == -1:
                        self.DownDPad = 1
                        self.UpDPad = 0
                    elif event.state == 1:
                        self.UpDPad = 1
                        self.DownDPad = 0
                    else:
                        self.DownDPad = 0
                        self.UpDPad = 0




if __name__ == '__main__':
    print('initiating GUI')
    tkinter_thread = threading.Thread(target=tk_function)
    tkinter_thread.start()
    print('connecting to camera 1')
    currentcam = Camera(ip1)
    print('connecting to ATEM')
    switcher = PyATEMMax.ATEMMax()
    switcher.connect(atem)
    switcher.waitForConnection()
    iscamera2 = False
    cam1active = False
    cam2active = False
    toProgram = False
    channel = 0
    print('connecting to controller')
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
            zoom = max(currentcam.get_zoom_position()/5000,1)
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
            zoom = max(currentcam.get_zoom_position()/5000,1)
            currentcam.pantilt(int(controller['x2'] * -12 / zoom), int(controller['y2'] * 12 / zoom))
            if controller['b2']:
                currentcam.zoom(int(controller['t2'] * -7))
            else:
                currentcam.zoom(int(controller['t2'] * 7))
        currentcam.get_zoom_position()
        if controller['c1'] or controller['c2'] or controller['c3'] or controller['c4'] or controller['A']:
            if controller['c1']:
                if channel == 0:
                    channel = 3
                if controller['c2']:
                    channel = 8
                if controller['c3']:
                    channel = 5
            elif controller['c2']:
                if channel == 0:
                    channel = 4
                if controller['c4']:
                    channel = 6
            elif controller['c3']:
                if channel == 0:
                    channel = 1
                if controller['c4']:
                    channel = 7
            elif controller['c4']:
                if channel == 0:
                    channel = 2
            elif controller['A']:
                toProgram = True
        elif channel:
            print(channel)
            ct.cancel()
            switcher.setPreviewInputVideoSource(0,channel)
            channel = 0
        elif toProgram:
            switcher.execCutME(0)
            toProgram = False
