import cv2
import time
from statistics import mean
from gaze_tracking import GazeTracking

def get_postition(h, v):
	#center h - >57, <64
	#center v - >78, <87
	#low v - >95
	#right - <50
	#left - >67
	if v <= 0.80: #upper
		if h >= 0.64: #left
			print('upper left')
		elif h <= 0.56: #right
			print('upper right')
		else: #center
			print('upper middle')
	else: #lower
		if h >= 0.64: #left
			print('lower left')
		elif h <= 0.56: #right
			print('lower right')
		else: #center
			print('lower middle')

def direction(gaze, webcam, pos):
	print(pos)
	time.sleep(3)

	h = []
	v = []
	for i in range(50):
		_, frame = webcam.read()
		gaze.refresh(frame)
		sh = gaze.horizontal_ratio()
		sv = gaze.vertical_ratio()
		if sh is not None:
			h.append(sh)
		if sv is not None:
			v.append(sv)

	print('samples - ' + str(len(h)))
	print('mean h - ' + str(mean(h)))
	print('mean v - ' + str(mean(v)))
	print('max h - ' + str(max(h)))
	print('min v - ' + str(max(v)))
	print('max h - ' + str(min(h)))
	print('min v - ' + str(min(v)))

	return (mean(h), mean(v))

def border(a, b):
	ah, av = a
	bh, bv = b
	return (mean([ah, bh]), mean([av, bv]))

def calibrate(gaze, webcam):
	ul = direction(gaze, webcam, 'upper left')
	um = direction(gaze, webcam, 'upper middle')
	ur = direction(gaze, webcam, 'upper right')
	cl = direction(gaze, webcam, 'center left')
	c = direction(gaze, webcam, 'center')
	cr = direction(gaze, webcam, 'center right')
	ll = direction(gaze, webcam, 'lower left')
	lm = direction(gaze, webcam, 'lower middle')
	lr = direction(gaze, webcam, 'lower right')

	print('borders')
	print('ul/um - ' + str(border(ul, um)))
	print('um/ur - ' + str(border(um, ur)))
	print('cl/c - ' + str(border(cl, c)))
	print('c/cr - ' + str(border(c, cr)))
	print('ll/lm - ' + str(border(ll, lm)))
	print('lm/lr - ' + str(border(lm, lr)))
	print('ul/cl - ' + str(border(ul, cl)))
	print('cl/ll - ' + str(border(cl, ll)))
	print('um/c - ' + str(border(um, c)))
	print('c/lm - ' + str(border(c, lm)))
	print('ur/cr - ' + str(border(ur, cr)))
	print('cr/lr - ' + str(border(cr, lr)))

	#get average for all upper values/upper to middle averages

def main():
	gaze = GazeTracking()
	webcam = cv2.VideoCapture(0)
	calibrate(gaze, webcam)

if __name__ == '__main__':
	main()
