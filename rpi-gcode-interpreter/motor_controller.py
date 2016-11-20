############################################################
#       IF YOU ARE SOMEBODY ELSE USING THIS CODE YOU       #
#       YOU WILL HAVE TO PROVIDE THESE FUNCTIONS YOURSELF  #
############################################################

import sys
import RPi.GPIO as GPIO


class MotorController:
    def __init__(self):

        # Distances in mm that each step of the stepper motor propels each axis
        self.mm_per_step = {'x': 0.000523, 'y': 0.000523, 'z': 0.000523}

        # This value will be used as speed for the 'rapid movement' of the machine
        # Measured in steps per second
        self.rapid_speed_maximum = 625.0

        # This value will be used as the fastest to move the machine when mill is lowered
        # Measured in steps per second
        self.work_speed_maximum = 625.0

        # These are the pins to control the L293D motor drivers for the CNC
        self.control_pins = {'x': (6, 19, 13, 26),
                             'y': (20, 12, 21, 16),
                             'z': (23, 27, 17, 22)}

        # Tracks how many steps have been taken on each axis at any point
        self.current_steps = {'x': 0, 'y': 0, 'z': 0}

        # Configure pinout options
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup motor control pins
        for pins in self.control_pins.values():
                GPIO.setup(pins, GPIO.OUT)

    def axis_step(self, axis, direction):

        # Interacts with the pins to move the motor to the next step

        # Releases holding torque power from previously powered pin
        GPIO.output(self.control_pins[axis][self.current_steps[axis] % 4], False)

        # Increments counter that keeps track of which part of the (4-phase) rotation cycle we are in
        self.current_steps[axis] += direction
        # print(str(axis) + ": " + str(self.current_steps[axis]))

        # Power next pin in phase to drive motor
        GPIO.output(self.control_pins[axis][self.current_steps[axis] % 4], True)

# Allows standalone running of the motor_controller script to move carts along axis by amount specified in args
# Syntax is <axis> <direction> <steps> eg python motor_controller.py x -1 2400
if __name__ == "__main__":
    motor_controller = MotorController()
    for i in range(0, sys.argv[3]):
        motor_controller.axis_step(sys.argv[1], sys.argv[2])
