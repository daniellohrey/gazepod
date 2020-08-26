import cv2, time
import PySimpleGUI as sg
from screeninfo import get_monitors
from statistics import mean
from gaze_tracking import GazeTracking

QLEN = 5
DLEN = 2
CLEN = 30

UM = 0.847
ML = 0.897
LM = 0.678
MR = 0.610

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
	window.read(timeout=20)
	time.sleep(1)

	h = []
	v = []
	i = 0
	while i < CLEN:
		window.read(timeout=20)
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
	window.read(timeout=20)

	#check number of samples (or collect until CLEN samples)

	#print('dir - ' + str(pos))
	#print('mean h - ' + str(mean(h)))
	#print('mean v - ' + str(mean(v)))

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

	s = str(int(ul[0] * 1000)) + '\t' + str(int(um[0] * 1000)) + '\t' + str(int(ur[0] * 1000)) + '\n\n'
	s += str(int(ul[1] * 1000)) + '\t' + str(int(um[1] * 1000)) + '\t' + str(int(ur[1] * 1000)) + '\n\n'
	s += str(int(cl[0] * 1000)) + '\t' + str(int(c[0] * 1000)) + '\t' + str(int(cr[0] * 1000)) + '\n\n'
	s += str(int(cl[1] * 1000)) + '\t' + str(int(c[1] * 1000)) + '\t' + str(int(cr[1] * 1000)) + '\n\n'
	s += str(int(ll[0] * 1000)) + '\t' + str(int(lm[0] * 1000)) + '\t' + str(int(lr[0] * 1000)) + '\n\n'
	s += str(int(ll[1] * 1000)) + '\t' + str(int(lm[1] * 1000)) + '\t' + str(int(lr[1] * 1000)) + '\n\n'

	#print('borders')
	#print('ul/um - ' + str(avd(ul, um, h=True)))
	#print('um/ur - ' + str(avd(um, ur, h=True)))
	#print('cl/c - ' + str(avd(cl, c, h=True)))
	#print('c/cr - ' + str(avd(c, cr, h=True)))
	#print('ll/lm - ' + str(avd(ll, lm, h=True)))
	#print('lm/lr - ' + str(avd(lm, lr, h=True)))
	#print('ul/cl - ' + str(avd(ul, cl, h=False)))
	#print('cl/ll - ' + str(avd(cl, ll, h=False)))
	#print('um/c - ' + str(avd(um, c, h=False)))
	#print('c/lm - ' + str(avd(c, lm, h=False)))
	#print('ur/cr - ' + str(avd(ur, cr, h=False)))
	#print('cr/lr - ' + str(avd(cr, lr, h=False)))

	#print('um - ' + str(um))
	#print('lm - ' + str(lm))
	#print('cr - ' + str(cr))
	#print('cl - ' + str(cl))

	#border of rows/columns
	UM0 = mean([avd(ul, cl, h=False), avd(um, c, h=False), avd(ur, cr, h=False)])
	UL1 = (lm[1] - um[1]) / 3
	UM1 = um[1] + UL1
	#UM = int(UM * 1000)
	ML0 = mean([avd(cl, ll, h=False), avd(c, lm, h=False), avd(cr, lr, h=False)])
	ML1 = um[1] + (2 * UL1)
	#ML = int(ML * 1000)
	LM0 = mean([avd(ul, um, h=True), avd(cl, c, h=True), avd(ll, lm, h=True)])
	LR1 = (cl[0] - cr[0]) / 3
	LM1 = cl[0] - LR1
	#LM = int(LM * 1000)
	MR0 = mean([avd(um, ur, h=True), avd(c, cr, h=True), avd(lm, lr, h=True)])
	MR1 = cl[0] - (2 * LR1)
	#MR = int(MR * 1000)

	#print('UM - ' + str(UM))
	#print('ML - ' + str(ML))
	#print('LM - ' + str(LM))
	#print('MR - ' + str(MR))

	s += 'UL1 - ' + str(int(UL1 * 1000)) + '\t'
	s += 'UM0 - ' + str(int(UM0 * 1000)) + ' '
	s += 'UM1 - ' + str(int(UM1 * 1000)) + '\t'
	s += 'ML0 - ' + str(int(ML0 * 1000)) + ' '
	s += 'ML1 - ' + str(int(ML1 * 1000)) + '\n\n'
	s += 'LR1 - ' + str(int(LR1 * 1000)) + '\t'
	s += 'LM0 - ' + str(int(LM0 * 1000)) + ' '
	s += 'LM1 - ' + str(int(LM1 * 1000)) + '\t'
	s += 'MR0 - ' + str(int(MR0 * 1000)) + ' '
	s += 'MR1 - ' + str(int(MR1 * 1000)) + '\n\n'

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
