#!/usr/bin/env python3
"""
motor_test_gui.py

GUI application to test individual stepper motors.
Select a motor, specify step count, and move forward or backward.
"""
import tkinter as tk
from tkinter import messagebox

try:
    from motor_controller import MotorController, Stepper
except ImportError:
    messagebox = None
    # In stub mode, define dummy Stepper
    class Stepper:
        FORWARD = "FORWARD"
        BACKWARD = "BACKWARD"

class MotorTestGUI:
    def __init__(self, master):
        self.master = master
        master.title("Motor Test GUI")

        # Initialize motor controller
        self.mc = MotorController()
        self.motors = list(self.mc.steppers.keys())

        # Motor selection dropdown
        tk.Label(master, text="Select Motor:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.selected_motor = tk.StringVar(master)
        self.selected_motor.set(self.motors[0])
        tk.OptionMenu(master, self.selected_motor, *self.motors).grid(row=0, column=1, padx=5, pady=5)

        # Step count entry
        tk.Label(master, text="Steps to move:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.step_entry = tk.Entry(master)
        self.step_entry.insert(0, "1")
        self.step_entry.grid(row=1, column=1, padx=5, pady=5)

        # Forward and Backward buttons
        self.forward_btn = tk.Button(master, text="Forward", command=self.step_forward)
        self.forward_btn.grid(row=2, column=0, padx=5, pady=10, sticky="ew")
        self.backward_btn = tk.Button(master, text="Backward", command=self.step_backward)
        self.backward_btn.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        tk.Label(master, textvariable=self.status_var).grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def step_forward(self):
        self._step(Stepper.FORWARD)

    def step_backward(self):
        self._step(Stepper.BACKWARD)

    def _step(self, direction):
        motor = self.selected_motor.get()
        try:
            count = int(self.step_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter an integer step count.")
            return
        for _ in range(abs(count)):
            self.mc._step_multiple([motor], direction)
        self.status_var.set(f"Moved {motor} {count} steps {'+' if direction==Stepper.FORWARD else '-'}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MotorTestGUI(root)
    root.mainloop()
