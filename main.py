import cv2, time
import PySimpleGUI as sg
from screeninfo import get_monitors
from statistics import mean
from gaze_tracking import GazeTracking

QLEN = 8 #samples before mean direction
DLEN = 3 #directions before selection
CLEN = 30 #samples for calibration
TO = 20 #timeout for gui
DEBUG = 0 #debug verbosity level

UM = None
ML = None
LM = None
MR = None

def get_dir(h, v):
	if v <= UM:
		if h >= LM:
			return 0
		elif h <= MR:
			return 2
		else:
			return 1
	elif v >= ML:
		if h >= LM:
			return 6
		elif h <= MR:
			return 8
		else:
			return 7
	else:
		if h >= LM:
			return 3
		elif h <= MR:
			return 5
		else:
			return 4

def cal_dir(gaze, webcam, window, pos):
	key = 'img' + str(pos)
	window[key].update(visible=False)
	window.read(timeout=TO)
	time.sleep(1)

	h = []
	v = []
	i = 0
	while i < CLEN:
		window.read(timeout=TO)
		_, frame = webcam.read()
		gaze.refresh(frame)
		sh = gaze.horizontal_ratio()
		sv = gaze.vertical_ratio()
		if sh is not None:
			h.append(sh)
		else:
			continue
		if sv is not None:
			v.append(sv)
		else:
			continue
		i += 1

	window[key].update(visible=True)
	window.read(timeout=TO)

	return (mean(h), mean(v))

def avd(a, b, h=True):
	ah, av = a
	bh, bv = b
	if h:
		return mean([ah, bh])
	else: #v
		return mean([av, bv])

def calibrate(gaze, webcam, window):
	global UM, ML, LM, MR

	ul = cal_dir(gaze, webcam, window, 0)
	um = cal_dir(gaze, webcam, window, 1)
	ur = cal_dir(gaze, webcam, window, 2)
	cl = cal_dir(gaze, webcam, window, 3)
	c = cal_dir(gaze, webcam, window, 4)
	cr = cal_dir(gaze, webcam, window, 5)
	ll = cal_dir(gaze, webcam, window, 6)
	lm = cal_dir(gaze, webcam, window, 7)
	lr = cal_dir(gaze, webcam, window, 8)

	#border of rows/columns
	UM = mean([avd(ul, cl, h=False), avd(um, c, h=False), avd(ur, cr, h=False)])
	ML = mean([avd(cl, ll, h=False), avd(c, lm, h=False), avd(cr, lr, h=False)])
	LM = mean([avd(ul, um, h=True), avd(cl, c, h=True), avd(ll, lm, h=True)])
	MR = mean([avd(um, ur, h=True), avd(c, cr, h=True), avd(lm, lr, h=True)])

	if DEBUG >= 1:
		s = str(int(ul[0] * 1000)) + '\t' + str(int(um[0] * 1000)) + '\t' + str(int(ur[0] * 1000)) + '\n'
		s += str(int(ul[1] * 1000)) + '\t' + str(int(um[1] * 1000)) + '\t' + str(int(ur[1] * 1000)) + '\n\n'
		s += str(int(cl[0] * 1000)) + '\t' + str(int(c[0] * 1000)) + '\t' + str(int(cr[0] * 1000)) + '\n'
		s += str(int(cl[1] * 1000)) + '\t' + str(int(c[1] * 1000)) + '\t' + str(int(cr[1] * 1000)) + '\n\n'
		s += str(int(ll[0] * 1000)) + '\t' + str(int(lm[0] * 1000)) + '\t' + str(int(lr[0] * 1000)) + '\n'
		s += str(int(ll[1] * 1000)) + '\t' + str(int(lm[1] * 1000)) + '\t' + str(int(lr[1] * 1000)) + '\n\n'
		s += 'LM - ' + str(int(LM * 1000)) + '\t'
		s += 'MR - ' + str(int(MR * 1000)) + '\n\n'
		s += 'UM - ' + str(int(UM * 1000)) + '\n'
		s += 'ML - ' + str(int(ML * 1000)) + '\n'
		print(s)

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
		e, val = window.read(timeout=TO) 
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
			s = get_dir(mean(h), mean(v))
			key = 'img' + str(s)
			window[key].update(visible=False)
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
			window[key].update(visible=True)
		else:
			#set background color of d[0]
			pass

	window.close()

if __name__ == '__main__':
	main()
