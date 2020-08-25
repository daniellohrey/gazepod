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
	if h <= UM:
		if v >= LM:
			return 0
		elif v <= MR:
			return 2
		else:
			return 1
	elif h >= ML:
		if v >= LM:
			return 6
		elif v <= MR:
			return 8
		else:
			return 7
	else:
		if v >= LM:
			return 3
		elif v <= MR:
			return 5
		else:
			return 4

def cal_dir(gaze, webcam, window, pos):
	key = 'img' + str(pos)
	window[key].update(visible=False)
	window.read(timeout=20)
	time.sleep(1)

	h = []
	v = []
	for i in range(CLEN):
		window.read(timeout=20)
		_, frame = webcam.read()
		gaze.refresh(frame)
		sh = gaze.horizontal_ratio()
		sv = gaze.vertical_ratio()
		if sh is not None:
			h.append(sh)
		if sv is not None:
			v.append(sv)

	window[key].update(visible=True)
	window.read(timeout=20)

	#check number of samples (or collect until CLEN samples)

	print('samples - ' + str(len(h)))
	print('mean h - ' + str(mean(h)))
	print('mean v - ' + str(mean(v)))

	return (mean(h), mean(v))

def avd(a, b, h=True):
	ah, av = a
	bh, bv = b
	if h:
		return mean([ah, bh])
	else: #v
		return mean([av, bv])

def calibrate(gaze, webcam, window):
	#get average values for all directions
	#change pos to integer
	#change lower to bottom?
	ul = cal_dir(gaze, webcam, window, 0)
	um = cal_dir(gaze, webcam, window, 1)
	ur = cal_dir(gaze, webcam, window, 2)
	cl = cal_dir(gaze, webcam, window, 3)
	c = cal_dir(gaze, webcam, window, 4)
	cr = cal_dir(gaze, webcam, window, 5)
	ll = cal_dir(gaze, webcam, window, 6)
	lm = cal_dir(gaze, webcam, window, 7)
	lr = cal_dir(gaze, webcam, window, 8)

	print('borders')
	print('ul/um - ' + str(avd(ul, um, h=True)))
	print('um/ur - ' + str(avd(um, ur, h=True)))
	print('cl/c - ' + str(avd(cl, c, h=True)))
	print('c/cr - ' + str(avd(c, cr, h=True)))
	print('ll/lm - ' + str(avd(ll, lm, h=True)))
	print('lm/lr - ' + str(avd(lm, lr, h=True)))
	print('ul/cl - ' + str(avd(ul, cl, h=False)))
	print('cl/ll - ' + str(avd(cl, ll, h=False)))
	print('um/c - ' + str(avd(um, c, h=False)))
	print('c/lm - ' + str(avd(c, lm, h=False)))
	print('ur/cr - ' + str(avd(ur, cr, h=False)))
	print('cr/lr - ' + str(avd(cr, lr, h=False)))

	#border of rows/columns
	UM = mean([avd(ul, cl, h=False), avd(um, c, h=False), avd(ur, cr, h=False)])
	UM = int(UM * 100)
	ML = mean([avd(cl, ll, h=False), avd(c, lm, h=False), avd(cr, lr, h=False)])
	ML = int(ML * 100)
	LM = mean([avd(ul, um, h=True), avd(cl, c, h=True), avd(ll, lm, h=True)])
	LM = int(LM * 100)
	MR = mean([avd(um, ur, h=True), avd(c, cr, h=True), avd(lm, lr, h=True)])
	MR = int(MR * 100)

	print('UM - ' + str(UM))
	print('ML - ' + str(ML))
	print('LM - ' + str(LM))
	print('MR - ' + str(MR))

def main():
	m = get_monitors()[0]
	h, w = m.height, m.width
	h = ((h - (h % 3)) / 3) - 45 #adjust for different screen size
	w = ((w - (w % 3)) / 3) - 35

	sg.theme('DarkGrey3')
	layout = [[sg.Frame('', [[sg.Image('images/test.png', size=(w, h), key='img'+str(fr*3+fc))]], pad=(5, 5), background_color='yellow', key='frm'+str(fr*3+fc)) for fc in range(3)] for fr in range(3)]
	layout.extend([[sg.Button('Exit', size=(10, 1), font='Helvetica 14')]])
	#update image with update(filename='')
	#enable events for images so theyre clickable
	window = sg.Window('GazePOD', layout, finalize=True, resizable=True)
	#window.Maximize()

	gaze = GazeTracking()
	webcam = cv2.VideoCapture(0)
	calibrate(gaze, webcam, window)

	h = []
	v = []
	d = []
	i = 0
	while True:
		#get event or timeout
		e, val = window.read(timeout=20) 
		if e == 'Exit' or e == sg.WIN_CLOSED:
			break
		elif e == 'Calibrate':
			calibrate(gaze, webcam, window)
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
		else:
			continue
		if sv is not None:
			v.append(sv)
			if len(v) > QLEN:
				v.pop(0)
		else:
			continue

		#get average gaze direction
		if i == QLEN:
			i =- QLEN
			s = get_direction(h, v)
			d.append(s)
			if len(d) > DLEN:
				d.pop(0)
		else:
			i += 1
			continue

		#select image
		if d.count(d[0]) == len(d):
			#select direction
			key = 'img' + str(d[0])
			window[key].update(visible=False)
		else:
			#set background color of d[0]
			pass

	window.close()

if __name__ == '__main__':
	main()
