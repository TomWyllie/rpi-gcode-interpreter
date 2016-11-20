import time
import math
import sys
from threading import Thread
import motor_controller as mc


class Interpreter:

    def __init__(self):

        # Initialise file data list
        self.gcode_data_list = []

        # gcode_path = read_from_args
        # self.load_gcode_from_file("test.gcode")
        self.load_gcode_from_file(sys.argv[1])

        # Instantiate motor controller objects
        self.mc = mc.MotorController()

        # Store the different axes in use
        self.axes = ('x', 'y', 'z')
        self.axes_thread = {}
        self.line_count = 0
        self.line_counter = 0

        self.interpret_data()

    def load_gcode_from_file(self, path):
        with open(path) as f:
            for line in f.readlines():
                if line[0] != "(":
                    self.gcode_data_list.append(line.split())

    def interpret_data(self):
        self.line_count = len(self.gcode_data_list)
        for line in self.gcode_data_list:
            self.line_counter += 1
            try:
                point_data = []
                for arg in line:
                    if arg[0] == "N":
                        pass
                    elif arg[0].lower() == 'g' or arg[0].lower() == 'm':
                        code = arg
                    else:
                        for axis in self.axes:
                            if arg[0].lower() == axis:
                                point_data.append((axis, arg[1:]))
                    # Stores argument in case it is none of the above and required by a single parameter Gcode function
                    param = arg

                if code == "G0":
                    self.move_to_coords(point_data, self.mc.rapid_speed_maximum)
                elif code == "G1":
                    self.move_to_coords(point_data, self.mc.work_speed_maximum)
                elif code == "G4":
                    time.sleep(param)
            except TypeError:
                print("Unsupported or Malformed GCode: "),
                print(line)
                print("Skipping command...")
        print("\nFinished processing GCode file!")

    def move_to_coords(self, point_data, speed):

        axis_deltas = []
        greatest_delta = 0
        for axis in point_data:
            # Get current steps of this axis
            current_steps = self.mc.current_steps[axis[0]]

            # Get the number of steps away from the origin that the requested point is at
            target_steps = float(axis[1]) / self.mc.mm_per_step[axis[0]]

            # Determine required direction to move in
            direction = int(target_steps > current_steps)
            if direction == 0: direction = -1

            # Get the required steps that we need to take on this axis to reach the target point
            delta_steps = int(math.fabs(target_steps - current_steps))

            # Check if this axis has the largest motion of any so far - this determines the 'limiting' axis that will
            # reach that maximum speed limit and which all others will have to slow down for
            if delta_steps > greatest_delta:
                greatest_delta = delta_steps

            # Catches axes with no change in them
            if delta_steps != 0:
                axis_deltas.append((axis[0], delta_steps, direction))

        # Determine how many seconds this movement will take
        motion_duration = greatest_delta / speed

        threads = []

        # Create threads to carry out this motion
        for axis in axis_deltas:
            threads.append(StepperThread(axis[0], axis[1], axis[2], motion_duration, self))

        # Set threads running
        for thread in threads:
            thread.start()

        # Wait for threads to finish
        for thread in threads:
            thread.join()


class StepperThread(Thread):
        def __init__(self, axis, steps, direction, motion_duration, interpreter):
            Thread.__init__(self)
            self.axis = axis
            self.steps = steps
            self.direction = direction
            self.motion_duration = motion_duration
            self.mc = interpreter.mc
            self.interpreter = interpreter

        def run(self):
            space_time = self.motion_duration / self.steps
            for i in range(0, self.steps):
                self.mc.axis_step(self.axis, self.direction)
                time.sleep(space_time)
                info = "Processing line " + str(self.interpreter.line_counter) + " / " + str(self.interpreter.line_count)
                for axis in self.interpreter.axes:
                    info += ("\t\t" + str(axis.upper()) + ":" + str(self.mc.current_steps[axis]))
                sys.stdout.write("\r" + info)
                sys.stdout.flush()


if __name__ == "__main__":
    interpreter = Interpreter()