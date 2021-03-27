# import board
# import busio
# import adafruit_pca9685

import time

from adafruit_servokit import ServoKit

# i2c = busio.I2C(board.SCL, board.SDA)
# hat = adafruit_pca9685.PCA9685(i2c)

kit = ServoKit(channels=16)

kit.continuous_servo[0].throttle = -1.0
kit.continuous_servo[1].throttle =  1.0

time.sleep(2.0)

kit.continuous_servo[0].throttle = 0
kit.continuous_servo[1].throttle = 0

time.sleep(2.0)

kit.continuous_servo[0].throttle =  0.5
kit.continuous_servo[1].throttle = -0.5

time.sleep(2.0)

kit.continuous_servo[0].throttle = 0
kit.continuous_servo[1].throttle = 0


