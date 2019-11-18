#Object detection and tracking with OpenCV
#==> Real Time tracking with Goal Keeper Servo 

#Based on original tracking object code developed by Adrian Rosebrock
# import the necessary packages

from __future__ import print_function
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import os
import RPi.GPIO as GPIO

# define Servos GPIOs
panServo = 27

#position servos 

def positionServo (servo, angle):
    os.system("python angleServoCtrl.py " + str(servo) + " " + str(angle))
    print("[INFO] Positioning servo at GPIO {0} to {1} degrees\n".format(servo, angle))

# position servos to present object at center of the frame


def mapServoPosition (x, y):
    global panAngle

if (x < 220):
        panAngle += 10
        if panAngle > 140:
            panAngle = 140
        positionServo (panServo, panAngle)
 
    if (x > 280):
        panAngle -= 10
        if panAngle < 40:
            panAngle = 40
        positionServo (panServo, panAngle)


# initialize the video stream and allow the camera sensor to warmup

print("[INFO] waiting for camera to warmup...")
vs = VideoStream(0).start()
time.sleep(2.0)

# define the lower and upper boundaries of the object
# to be tracked in the HSV color space

colorLower = (24, 100, 100)
colorUpper = (44, 255, 255)


# Initialize angle servos at 90-90 position

global panAngle
panAngle = 90


# positioning Pan/Tilt servos at initial position
positionServo (panServo, panAngle)


# loop over the frames from the video stream
while True:
	# grab the next frame from the video stream, Invert 180o, resize the
	# frame, and convert it to the HSV color space
	frame = vs.read()
	frame = imutils.resize(frame, width=500)
	frame = imutils.rotate(frame, angle=180)
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	# construct a mask for the object color, then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, colorLower, colorUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the object
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	center = None

	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)
			
			# position Servo at center of circle
			mapServoPosition(int(x), int(y))
			

	# show the frame to our screen
	cv2.imshow("Frame", frame)
	
	# if [ESC] key is pressed, stop the loop
	key = cv2.waitKey(1) & 0xFF
	if key == 27:
            break

# do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff \n")
positionServo (panServo, 90)

GPIO.cleanup()
cv2.destroyAllWindows()
vs.stop()
