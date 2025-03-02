from Action import *
from Line_Tracking import *
import time
import RPi.GPIO as GPIO

class Remove_Obstacles:
    def __init__(self):
        self.IR01 = 16
        self.IR02 = 20
        self.IR03 = 21
        self.servo = Servo()
        self.PWM = Motor()
        self.distance = Ultrasonic()
        self.infrared = Line_Tracking()
        self.action = ServoMode()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.IR01, GPIO.IN)
        GPIO.setup(self.IR02, GPIO.IN)
        GPIO.setup(self.IR03, GPIO.IN)

    def run_Move(self):
        self.action.ServoMode('1')
        self.PWM.setMotorModel(-1500, 1500)  # Left turn
        time.sleep(1.5)
        self.PWM.setMotorModel(0, 0)  # Stop
        self.action.ServoMode('2')
        self.PWM.setMotorModel(1500, -1500)  # Right turn
        time.sleep(1.4)

    def run_Line(self):
        self.LMR = 0x00
        if GPIO.input(self.IR01):
            self.LMR |= 4
        if GPIO.input(self.IR02):
            self.LMR |= 2
        if GPIO.input(self.IR03):
            self.LMR |= 1

        # Back off behavior when any sensor detects a black line.
        if self.LMR != 0:
            self.PWM.setMotorModel(0, 0)  # Stop
            time.sleep(0.5)              # Short pause
            self.PWM.setMotorModel(-1200, -1200)  # Back up
            time.sleep(1)                # Back up for 1 second
            self.run_Move()              # Optionally change direction after backing up
            return  # Skip further line following logic

    def run_Action(self):
        distance = self.distance.get_distance()
        # print("Obstacle distance is " + str(distance) + "CM")
        self.run_Line()
        if distance > 5.0 and distance <= 12.0:
            self.PWM.setMotorModel(0, 0)  # Stop
            time.sleep(0.01)
            self.run_Move()
        elif distance > 0.0 and distance <= 5.0:
            self.PWM.setMotorModel(-1200, -1200)  # Back up

    def run(self):
        time.sleep(1.5)
        while True:
            self.run_Action()

auto_Clear = Remove_Obstacles()

if __name__ == '__main__':
    print('Program is starting ... ')
    try:
        auto_Clear.run()
    except KeyboardInterrupt:
        auto_Clear.PWM.setMotorModel(0, 0)  # Stop
        auto_Clear.servo.setServoPwm('0', 90)
        auto_Clear.servo.setServoPwm('1', 140)
        print("\nEnd of program")