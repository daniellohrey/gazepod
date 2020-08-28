class Pod():
	def __init__(self, state=None, debug=0):
		""" Pod
		Options:
			state - list of initial images (must be subsequently created with add)
			debug - debug verbosity level
				1 - 
				2 - initial state
				3 - direction
				4 - next state
		"""

		self._DEBUG = debug
		self.items = {}

		if state == None:
			self._STATE = ['1'] * 9
		else:
			self._STATE = state
		if self._DEBUG >= 2:
			print(self._STATE)

	def get_state(self, d):
		""" Get state.
		Take a direction and return image in that direction.
		"""

		return self._STATE[d]

	def next_state(self):
		""" State iterator.
		Return all state one at a time as iterator.
		"""

		for s in self._STATE:
			if self._DEBUG >= 4:
				print(s)
			yield s

	def select(self, d):
		""" Select direction.
		Takes a direction and updates the state of the Pod.
		"""
		if self._DEBUG >= 3:
			print('dir - ' + str(d))
			print('img - ' + self._STATE[d])
		if self._STATE[0] == '1':
			self._STATE = ['2'] * 9
		else:
			self._STATE = ['1'] * 9
		return

		self._STATE = []
		for item in self.items[self._STATE[d]]:
			self._STATE.append(item)

	def add(self, name, points):
		""" Add item to Pod.
		Takes a name (with a corresponding image) and a list of other names with this item points to (also created with add).
		"""

		self.items[name] = points

	def mass_add(self, filename):
		""" Mass add items from file.
		Takes a csv filename with first value being item name followed by items it points to (also created with add).
		"""

		pass

if __name__ == '__main__':
	print('This class is used by Tracker.')
