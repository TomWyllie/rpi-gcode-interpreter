############################################################
#       IF YOU ARE SOMEBODY ELSE USING THIS CODE YOU       #
#       YOU WILL HAVE TO PROVIDE THESE FUNCTIONS YOURSELF  #
############################################################

import RPi.GPIO as GPIO


class MotorController:
    def __init__(self):

        # Distances in mm that each step of the stepper motor propels each axis
        self.distances_per_step = {'x': 0.1, 'y': 0.1, 'z': 0.1}

        # These are the pins to control the L293D motor drivers for the CNC
        self.control_pins = {'x': (6, 19, 13, 26),
                             'y': (20, 12, 21, 16),
                             'z': (23, 27, 17, 22)}

        # Tracks how many steps have been taken on each axis at any point
        self.current_steps = {'x': 0, 'y': 0, 'z': 0}

        # Configure pin out options
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup motor control pins
        for pins in self.control_pins:
            for pin in pins:
                GPIO.setup(pin, GPIO.OUT)

    def axis_step(self, axis, direction):

        # Interacts with the pins to move the motor to the next step

        # Releases holding torque power from previously powered pin
        GPIO.output(self.control_pins[axis][self.current_steps[axis] % 4], False)

        # Increments counter that locally keeps track of which part of the (4-phase) rotation cycle we are in
        self.current_steps[axis] += direction

        # Power next pin in phase to drive motor
        GPIO.output(self.control_pins[axis][self.current_steps[axis] % 4], True)
