import cv2, time
import PySimpleGUI as sg
from screeninfo import get_monitors
from statistics import mean
from gaze_tracking import GazeTracking

QLEN = 10
DLEN = 3
CLEN = 50

UM = None
ML = None
LM = None
MR = None

def get_postition(h, v):
	pass

def direction(gaze, webcam, pos):
	print(pos)
	time.sleep(3)

	h = []
	v = []
	for i in range(CLEN):
		_, frame = webcam.read()
		gaze.refresh(frame)
		sh = gaze.horizontal_ratio()
		sv = gaze.vertical_ratio()
		if sh is not None:
			h.append(sh)
		if sv is not None:
			v.append(sv)

	#check number of samples (or collect until CLEN samples)

	print('samples - ' + str(len(h)))
	print('mean h - ' + str(mean(h)))
	print('mean v - ' + str(mean(v)))
	print('max h - ' + str(max(h)))
	print('min v - ' + str(max(v)))
	print('max h - ' + str(min(h)))
	print('min v - ' + str(min(v)))

	return (mean(h), mean(v))

def avd(a, b, h=True):
	ah, av = a
	bh, bv = b
	if h:
		return mean([ah, bh])
	else: #v
		return mean([av, bv])

def calibrate(gaze, webcam):
	#get average values for all directions
	#change pos to integer
	#change lower to bottom?
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

	#border of rows/columns
	UM = mean([avd(ul, cl, h=False), avd(um, c, h=False), avd(ur, cr, h=False)])
	ML = mean([avd(cl, ll, h=False), avd(c, lm, h=False), avd(cr, lr, h=False)])
	LM = mean([avd(ur, um, h=True), avd(cr, c, h=True), avd(lr, lm, h=True)])
	MR = mean([avd(um, ur, h=True), avd(c, cr, h=True), avd(lm, lr, h=True)])
	#scale

def main():
	m = get_monitors()[0]
	h, w = m.height, m.width
	h = ((h - (h % 3)) / 3) - 45 #adjust for different screen size
	w = ((w - (w % 3)) / 3) - 35

	sg.theme('DarkGrey3')
	layout = [[sg.Frame('', [[sg.Image('images/test.png', size=(w, h), key='img'+str(fr*3+fc))]], pad=(5, 5), background_color='yellow', key='frm'+str(fr*3+fc)) for fc in range(3)] for fr in range(3)]
	layout.extend = [[sg.Button('Exit', size=(10, 1), font='Helvetica 14')]]	
	#update image with update(filename='')
	#enable events for images so theyre clickable
	window = sg.Window('GazePOD', layout, finalize=True, resizable=True)
	#window.Maximize()

	gaze = GazeTracking()
	webcam = cv2.VideoCapture(0)
	calibrate(gaze, webcam)

	h = []
	v = []
	d = []
	i = 0
	while True:
		#get event or timeout
		e, v = window.read(timeout=20) 
		if e == 'Exit' or e == sg.WIN_CLOSED:
			break
		elif e == 'Calibrate':
			calibrate(gaze, webcam)
			continue

		#get frame and gaze
		_, frame = webcam.read()
		gaze.refresh(frame)
		sh = gaze.horizontal_ratio()
		sv = gaze.vertical_ratio()

		#add to queue
		if sh is not None:
			h.append(sh)
			if len(h) > QLEN:
				h.pop(0)
		if sv is not None:
			v.append(sv)
			if len(v) > QLEN:
				v.pop(0)

		#get average gaze direction
		if i == QLEN:
			i =- QLEN
			s = get_direction(h, v)
			d.append(s)
			if len(d) > DLEN:
				d.pop(0)

		#select image
		if d.count(d[0]) == len(d):
			select(d[0])
		else:
			#set background color of d[0]
			pass

	window.close()

if __name__ == '__main__':
	main()
