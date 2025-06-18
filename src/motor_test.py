"""
motor_test.py

Interactive script to spin individual stepper motors for validation.
Allows selecting a motor by name and issuing a specified number of microsteps.
"""
import time
from motor_controller import MotorController, Stepper

def main():
    mc = MotorController()
    motors = list(mc.steppers.keys())

    print("Available motors:")
    for idx, name in enumerate(motors):
        print(f"  {idx}: {name}")

    while True:
        choice = input("Select motor index to test (or 'q' to quit): ")
        if choice.lower() in ('q', 'quit', 'exit'):
            print("Exiting motor test.")
            break
        try:
            idx = int(choice)
            motor_name = motors[idx]
        except (ValueError, IndexError):
            print("Invalid selection. Try again.")
            continue

        step_input = input(
            "Enter number of steps (positive for FORWARD, negative for BACKWARD): "
        )
        try:
            steps = int(step_input)
        except ValueError:
            print("Invalid step count. Enter an integer.")
            continue

        direction = Stepper.FORWARD if steps > 0 else Stepper.BACKWARD
        num_steps = abs(steps)

        print(f"Stepping motor '{motor_name}' {steps} steps...")
        for _ in range(num_steps):
            mc._step_motor(motor_name, direction)
            time.sleep(mc.step_delay)
        print(f"Completed {steps} steps on '{motor_name}'. Current position: X={mc.position['x']:.2f} mm, Z={mc.position['z']:.2f} mm\n")

if __name__ == "__main__":
    main()
