'''
motor_controller.py

Provides MotorController for AeroVision project.
Abstracts stepper motor control for X and Z axes using Adafruit MotorKit.
Supports stub mode when hardware libraries are unavailable.
'''

import os
import yaml
import time

# Try to import real hardware libraries; fall back to stub mode otherwise
try:
    from adafruit_motorkit import MotorKit
    from adafruit_motor import stepper as Stepper
    REAL_HARDWARE = True
except ImportError:
    REAL_HARDWARE = False
    # Dummy Stepper constants for stub mode
    class Stepper:
        # Direction flags
        FORWARD = "FORWARD"
        BACKWARD = "BACKWARD"
        # Step styles
        SINGLE = "SINGLE"
        DOUBLE = "DOUBLE"
        INTERLEAVE = "INTERLEAVE"
        MICROSTEP = "MICROSTEP"

class MotorController:
    """
    High-level controller for two horizontal (X) and one vertical (Z) stepper motors.
    """
    def __init__(self, config_path=None):
        # Determine configuration file path
        if config_path is None:
            here = os.path.dirname(__file__)
            repo_root = os.path.abspath(os.path.join(here, os.pardir))
            config_path = os.path.join(repo_root, "config", "config.yaml")
        # Load configuration
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)

        # Setup stepping style and calibration
        self.step_style = getattr(Stepper, cfg.get("step_style", "SINGLE"))
        self.step_delay = cfg.get("step_delay", 0.01)
        self.steps_per_mm_x = cfg["calibration"].get("steps_per_mm_x", 80)
        self.steps_per_mm_z = cfg["calibration"].get("steps_per_mm_z", 100)

        # Initialize hardware interface
        if REAL_HARDWARE:
            self.kit = MotorKit()
        else:
            self.kit = None

        # Create stepper objects (or placeholders)
        self._init_steppers(cfg.get("motors", {}))

        # Track physical position in millimeters
        self.position = {"x": 0.0, "z": 0.0}

    def _init_steppers(self, channels):
        """
        Build a mapping from motor names to MotorKit stepper channels.
        channels: dict with keys 'x_left','x_right','z_axis' and channel numbers.
        """
        self.steppers = {}
        for name, channel in channels.items():
            attr = f"stepper{channel}"
            if REAL_HARDWARE and hasattr(self.kit, attr):
                self.steppers[name] = getattr(self.kit, attr)
            else:
                self.steppers[name] = None

    def _step_motor(self, name, direction):
        """
        Step a single motor one microstep.
        name: key in self.steppers; direction: Stepper.FORWARD/BACKWARD
        """
        stepper_obj = self.steppers.get(name)
        if REAL_HARDWARE and stepper_obj:
            stepper_obj.onestep(style=self.step_style, direction=direction)
        else:
            print(f"[STUB] Step motor '{name}' dir={direction}")

    def _step_multiple(self, names, direction):
        """
        Step multiple motors in sync, then delay.
        names: list of motor name strings.
        """
        for nm in names:
            self._step_motor(nm, direction)
        time.sleep(self.step_delay)

    def move_x(self, mm):
        """
        Move both X-axis motors by mm (positive=right, negative=left).
        """
        steps = int(round(mm * self.steps_per_mm_x))
        if steps == 0:
            return
        direction = Stepper.FORWARD if steps > 0 else Stepper.BACKWARD
        for _ in range(abs(steps)):
            self._step_multiple(["x_left", "x_right"], direction)
        self.position["x"] += mm

    def move_z(self, mm):
        """
        Move Z-axis motor by mm (positive=up, negative=down).
        """
        steps = int(round(mm * self.steps_per_mm_z))
        if steps == 0:
            return
        direction = Stepper.FORWARD if steps > 0 else Stepper.BACKWARD
        for _ in range(abs(steps)):
            self._step_multiple(["z_axis"], direction)
        self.position["z"] += mm

    def move_to(self, x_mm, z_mm):
        """
        Move from current (x,z) to target along straight path using Bresenham-like algorithm.
        """
        dx = x_mm - self.position["x"]
        dz = z_mm - self.position["z"]
        x_steps = int(round(dx * self.steps_per_mm_x))
        z_steps = int(round(dz * self.steps_per_mm_z))
        sx = Stepper.FORWARD if x_steps > 0 else Stepper.BACKWARD
        sz = Stepper.FORWARD if z_steps > 0 else Stepper.BACKWARD
        x_steps = abs(x_steps)
        z_steps = abs(z_steps)
        err = x_steps - z_steps

        x = z = 0
        while x < x_steps or z < z_steps:
            e2 = err * 2
            if x < x_steps and e2 > -z_steps:
                self._step_multiple(["x_left", "x_right"], sx)
                err -= z_steps
                x += 1
            if z < z_steps and e2 < x_steps:
                self._step_multiple(["z_axis"], sz)
                err += x_steps
                z += 1

        self.position["x"] = x_mm
        self.position["z"] = z_mm
