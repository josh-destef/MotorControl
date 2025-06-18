#!/usr/bin/env python3
"""
manual_gui.py

GUI control panel for AeroVision stepper rig.
Allows manual jogging of X and Z axes, emergency stop, home (aesthetic),
loading of CSV waypoint files, and dynamic step-size selection.
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Import the motor controller
from motor_controller import MotorController

class ManualControlApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AeroVision Manual Control")
        self.mc = MotorController()
        self.csv_path = None
        # Variable for dynamic step size
        self.step_size = tk.DoubleVar(value=1.0)
        self._create_widgets()

    def _create_widgets(self):
        # Step size selector
        step_frame = tk.Frame(self)
        step_frame.grid(row=0, column=0, columnspan=2, pady=(10,0))
        tk.Label(step_frame, text="Step Size (mm):").pack(side=tk.LEFT)
        tk.Spinbox(
            step_frame,
            from_=0.1,
            to=100.0,
            increment=0.1,
            textvariable=self.step_size,
            width=5
        ).pack(side=tk.LEFT, padx=(5,0))

        # X axis controls
        x_frame = tk.LabelFrame(self, text="X Axis", padx=10, pady=10)
        x_frame.grid(row=1, column=0, padx=10, pady=10)
        btn_left = tk.Button(
            x_frame, text="◀", width=4,
            command=lambda: self._move_x(-self.step_size.get())
        )
        btn_left.grid(row=0, column=0)
        self.lbl_x = tk.Label(x_frame, text=f"X = {self.mc.position['x']:.2f} mm")
        self.lbl_x.grid(row=0, column=1, padx=5)
        btn_right = tk.Button(
            x_frame, text="▶", width=4,
            command=lambda: self._move_x(self.step_size.get())
        )
        btn_right.grid(row=0, column=2)

        # Z axis controls
        z_frame = tk.LabelFrame(self, text="Z Axis", padx=10, pady=10)
        z_frame.grid(row=1, column=1, padx=10, pady=10)
        btn_up = tk.Button(
            z_frame, text="▲", width=4,
            command=lambda: self._move_z(self.step_size.get())
        )
        btn_up.grid(row=0, column=1)
        self.lbl_z = tk.Label(z_frame, text=f"Z = {self.mc.position['z']:.2f} mm")
        self.lbl_z.grid(row=1, column=1, pady=5)
        btn_down = tk.Button(
            z_frame, text="▼", width=4,
            command=lambda: self._move_z(-self.step_size.get())
        )
        btn_down.grid(row=2, column=1)

        # Control buttons
        ctrl_frame = tk.Frame(self)
        ctrl_frame.grid(row=2, column=0, columnspan=2, pady=10)
        btn_home = tk.Button(
            ctrl_frame, text="Home", width=8,
            command=self._home
        )
        btn_home.grid(row=0, column=0, padx=5)
        btn_estop = tk.Button(
            ctrl_frame, text="E-STOP", width=8, fg="white", bg="red",
            command=self._emergency_stop
        )
        btn_estop.grid(row=0, column=1, padx=5)
        btn_load = tk.Button(
            ctrl_frame, text="Load CSV", width=8,
            command=self._load_csv
        )
        btn_load.grid(row=0, column=2, padx=5)
        self.lbl_csv = tk.Label(
            ctrl_frame, text="No file loaded", anchor="w"
        )
        self.lbl_csv.grid(row=1, column=0, columnspan=3, pady=(5,0), sticky="we")

    def _move_x(self, distance):
        try:
            self.mc.move_x(distance)
            self._update_position()
        except Exception as e:
            messagebox.showerror("Error", f"X axis move failed: {e}")

    def _move_z(self, distance):
        try:
            self.mc.move_z(distance)
            self._update_position()
        except Exception as e:
            messagebox.showerror("Error", f"Z axis move failed: {e}")

    def _update_position(self):
        x = self.mc.position['x']
        z = self.mc.position['z']
        self.lbl_x.config(text=f"X = {x:.2f} mm")
        self.lbl_z.config(text=f"Z = {z:.2f} mm")

    def _home(self):
        # Aesthetic only: reset displayed position
        self.mc.position = {'x': 0.0, 'z': 0.0}
        self._update_position()
        messagebox.showinfo("Home", "Position reset to (0,0)")

    def _emergency_stop(self):
        # Disable all buttons
        for child in self.winfo_children():
            if isinstance(child, tk.Button) or isinstance(child, tk.Spinbox):
                child.config(state=tk.DISABLED)
        messagebox.showwarning("EMERGENCY STOP", "All controls disabled!")

    def _load_csv(self):
        path = filedialog.askopenfilename(
            title="Select CSV file", filetypes=[("CSV Files", "*.csv")]
        )
        if path:
            fname = os.path.basename(path)
            self.csv_path = path
            self.lbl_csv.config(text=f"Loaded: {fname}")
        else:
            self.lbl_csv.config(text="No file loaded")

if __name__ == "__main__":
    app = ManualControlApp()
    app.mainloop()
