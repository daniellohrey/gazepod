import cv2, time
import PySimpleGUI as sg
from screeninfo import get_monitors
from statistics import mean
from gaze_tracking import GazeTracking
from pod import Pod

class Tracker():
	def __init__(self, qlen=8, dlen=3, clen=30, to=20, debug=0, full_screen=False, theme='DarkGrey3', title='GazePOD'):
		""" Tracker
		Options:
			qlen - samples before mean direction
			dlen - directions before selection
			clen - samples for calibration
			to - timeout for gui
			debug - debug verbosity level
				1 - borders
				2 - calibration
				3 - direction
				4 - direction samples
			full_screen - make window full screen
			theme - PySimpleGUI theme
			title - window title
		"""

		self._QLEN = qlen
		self._DLEN = dlen
		self._CLEN = clen
		self._TO = to
		self._DEBUG = debug

		#borders
		self.UM = None
		self.ML = None
		self.LM = None
		self.MR = None

		self._calibrated = False

		m = get_monitors()[0]
		h, w = m.height, m.width
		h = ((h - (h % 3)) / 3) - 45 #TODO: adjust for different screen size
		w = ((w - (w % 3)) / 3) - 35

		sg.theme(theme)
		layout = [[sg.Frame('', [[sg.Image('images/test.png', size=(w, h), key='img'+str(fr*3+fc))]], pad=(5, 5), background_color='yellow', key='frm'+str(fr*3+fc)) for fc in range(3)] for fr in range(3)]
		layout.extend([[sg.Button('Exit', size=(10, 1), font='Helvetica 14')]])
		self.window = sg.Window(title, layout, finalize=True, resizable=True)
		if full_screen:
			window.Maximize()

		#padding color change
		#window['fr0'].Widget.config(padx=30)
		#window['fr0'].Widget.config(pady=30)
		#window['fr0'].Widget.config(background='red')

		self.pod = Pod(self.window)

		self.gaze = GazeTracking()
		self.webcam = cv2.VideoCapture(0)

	def _get_dir(self, h, v):
		""" Get direction of gaze
		Takes horizontal and vertical sample and returns direction of gaze.
		Requires prior calibration.
		Gazes:
			0  1  2

			3  4  5

			6  7  8
		"""
		if not self._calibrated:
			raise Exception('Not calibrated')

		if self._DEBUG >= 4:
			print('h - ' + str(h))
			print('v - ' + str(v))

		if v <= self.UM:
			if h >= self.LM:
				if self._DEBUG >= 3:
					print('dir - 0')
				return 0
			elif h <= self.MR:
				if self._DEBUG >= 3:
					print('dir - 2')
				return 2
			else:
				if self._DEBUG >= 3:
					print('dir - 1')
				return 1
		elif v >= self.ML:
			if h >= self.LM:
				if self._DEBUG >= 3:
					print('dir - 6')
				return 6
			elif h <= self.MR:
				if self._DEBUG >= 3:
					print('dir - 8')
				return 8
			else:
				if self._DEBUG >= 3:
					print('dir - 7')
				return 7
		else:
			if h >= self.LM:
				if self._DEBUG >= 3:
					print('dir - 3')
				return 3
			elif h <= self.MR:
				if self._DEBUG >= 3:
					print('dir - 5')
				return 5
			else:
				if self._DEBUG >= 3:
					print('dir - 4')
				return 4

	def _cal_dir(self, pos):
		""" Calibrates a particular direction.
		Takes gaze object, webcam, gui window (with required keys) and integer postition see get_dir for directions).
		"""

		key = 'img' + str(pos)
		#TODO: update image with calibration image
		self.window[key].update(visible=False)
		self.window.read(timeout=self._TO)
		time.sleep(1)

		h = []
		v = []
		i = 0
		while i < self._CLEN:
			e, val = self.window.read(timeout=self._TO)
			if e == 'Exit' or e == sg.WIN_CLOSED:
				break
			_, frame = self.webcam.read()
			self.gaze.refresh(frame)
			sh = self.gaze.horizontal_ratio()
			sv = self.gaze.vertical_ratio()
			if sh is not None and sv is not None:
				h.append(sh)
				v.append(sv)
			else:
				continue
			i += 1

		self.window[key].update(visible=True)
		self.window.read(timeout=self._TO)

		return (mean(h), mean(v))

	def calibrate(self):
		""" Calibrates the tracker.
		Takes a gaze object, a webcam and a window (with required keys).
		"""

		dirs = []
		for i in range(9):
			dirs.append(self._cal_dir(i))

		#border of rows/columns
		self.UM = mean([mean([dirs[0][0], dirs[3][0]]), mean([dirs[1][0], dirs[4][0]]), mean([dirs[2][0], dirs[5][0]])])
		self.ML = mean([mean([dirs[3][0], dirs[6][0]]), mean([dirs[4][0], dirs[7][0]]), mean([dirs[5][0], dirs[8][0]])])
		self.LM = mean([mean([dirs[0][1], dirs[1][1]]), mean([dirs[3][1], dirs[4][1]]), mean([dirs[6][1], dirs[7][1]])])
		self.MR = mean([mean([dirs[1][1], dirs[2][1]]), mean([dirs[4][1], dirs[5][1]]), mean([dirs[7][1], dirs[8][1]])])

		self._calibrated = True

		if self._DEBUG >= 2:
			s = str(int(dirs[0][0] * 1000)) + '\t' + str(int(dirs[1][0] * 1000)) + '\t' + str(int(dirs[3][0] * 1000)) + '\n'
			s += str(int(dirs[0][1] * 1000)) + '\t' + str(int(dirs[1][1] * 1000)) + '\t' + str(int(dirs[3][1] * 1000)) + '\n\n'
			s += str(int(dirs[3][0] * 1000)) + '\t' + str(int(dirs[4][0] * 1000)) + '\t' + str(int(dirs[5][0] * 1000)) + '\n'
			s += str(int(dirs[3][1] * 1000)) + '\t' + str(int(dirs[4][1] * 1000)) + '\t' + str(int(dirs[5][1] * 1000)) + '\n\n'
			s += str(int(dirs[6][0] * 1000)) + '\t' + str(int(dirs[7][0] * 1000)) + '\t' + str(int(dirs[8][0] * 1000)) + '\n'
			s += str(int(dirs[6][1] * 1000)) + '\t' + str(int(dirs[7][1] * 1000)) + '\t' + str(int(dirs[8][1] * 1000)) + '\n\n'
			print(s)
		if self._DEBUG >= 1:
			s = 'LM - ' + str(int(self.LM * 1000)) + '\t'
			s += 'MR - ' + str(int(self.MR * 1000)) + '\n\n'
			s += 'UM - ' + str(int(self.UM * 1000)) + '\n'
			s += 'ML - ' + str(int(self.ML * 1000)) + '\n'
			print(s)

	def loop(self):
		h = []
		v = []
		d = []
		while True:
			#get event or timeout
			e, val = self.window.read(timeout=self._TO) 
			if e == 'Exit' or e == sg.WIN_CLOSED:
				break
			elif e == 'Calibrate':
				self.calibrate()
				continue

			#get frame and gaze
			_, frame = self.webcam.read()
			self.gaze.refresh(frame)
			sh = self.gaze.horizontal_ratio()
			sv = self.gaze.vertical_ratio()

			#add to queue
			if sh is not None and sv is not None:
				h.append(sh)
				v.append(sv)
				if len(h) == self._QLEN:
					#get average gaze direction
					s = self._get_dir(mean(h), mean(v))
					key = 'img' + str(s)
					self.window[key].update(visible=False)
					#update frame background with
					#window['fr0'].Widget.config(background='red')
					#window['fr0'].Widget.config(highlightbackground='red')
					#window['fr0'].Widget.config(highlightcolor='red')
					d.append(s)
					if len(d) > self._DLEN:
						d.pop(0)
					h = []
					v = []
					time.sleep(0.5)
			else:
				continue

			#select image
			if d.count(d[0]) == len(d):
				#select direction
				key = 'img' + str(d[0])
				self.window[key].update(visible=True)
			else:
				#set background color of d[0]
				pass

		window.close()
		
if __name__ == '__main__':
	t = Tracker(debug=4)
	t.calibrate()
	t.loop()
