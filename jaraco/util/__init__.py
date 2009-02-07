# -*- coding: UTF-8 -*-

"""
jaraco.util:
  small functions or classes that don't have a home elsewhere
"""

__author__ = 'Jason R. Coombs <jaraco@sandia.gov>'
__version__ = '$Rev$'[6:-2]
__svnauthor__ = '$Author$'[9:-2]
__date__ = '$Date$'[7:-2]

import string, urllib, os
import re
import operator
import logging

log = logging.getLogger(__name__)

def CoerceType(value):
	"""
	CoerceType takes a value and attempts to convert it to a float, long, or int.
	If none of the conversions are successful, the original value is returned.
	
	>>> CoerceType('3')
	3
	
	>>> CoerceType('foo')
	'foo'
	"""
	result = value
	for transform in (float, long, int):
		try: result = transform(value)
		except ValueError: pass

	return result

def makeRows(list, nColumns):
	"""Make a list into rows of nColumns columns
	>>> makeRows([1, 2, 3, 4, 5], 2)
	[(1, 4), (2, 5), (3, None)]
	>>> makeRows([1, 2, 3, 4, 5], 3)
	[(1, 3, 5), (2, 4, None)]
	"""
	# calculate the minimum number of rows necessary to fit the list in n Columns
	nRows = len(list) / nColumns
	if len(list) % nColumns:
		nRows += 1
	# chunk the list into n Columns of length nRows
	result = chunkGenerator(list, nRows)
	# result is now a list of columns... transpose it to return a list of rows
	return map(None, *result)

def chunkGenerator(seq, size):
	"""Take a sequence and break it up into chunks of the specified size.
The last chunk may be smaller than size.
>>> tuple(chunkGenerator('foobarbaz', 3))
('foo', 'bar', 'baz')
>>> tuple(chunkGenerator([], 42))
()
>>> tuple(chunkGenerator(range(10), 3))
([0, 1, 2], [3, 4, 5], [6, 7, 8], [9])
"""
	for i in range(0, len(seq), size):
		yield seq[i:i+size]

import datetime

class QuickTimer(object):
	def __init__(self):
		self.Start()

	def Start(self):
		self.startTime = datetime.datetime.now()

	def Stop(self):
		return datetime.datetime.now() - self.startTime

def ReplaceList(object, substitutions):
	try:
		for old, new in substitutions:
			object = object.replace(old, new)
	except AttributeError:
		# object does not have a replace method
		pass
	return object

def ReverseLists(lists):
	tLists = zip(*lists)
	tLists.reverse()
	return zip(*tLists)

from jaraco import dateutil
import logging, time
class TimestampFileHandler(logging.StreamHandler):
	"""
	A logging handler which will log to a file, similar to
	logging.handlers.RotatingFileHandler, but instead of
	appending a number, uses a timestamp to periodically select
	new file names to log to.
	"""
	def __init__(self, baseFilename, mode='a', period='day'):
		self.baseFilename = baseFilename
		self.mode = mode
		self._setPeriod(period)
		logging.StreamHandler.__init__(self, None)

	def _setPeriod(self, period):
		"""
		Set the period for the timestamp.  If period is 0 or None, no period will be used.
		"""
		self._period = period
		if period:
			self._periodSeconds = dateutil.get_period_seconds(self._period)
			self._dateFormat = dateutil.get_date_format_string(self._periodSeconds)
		else:
			self._periodSeconds = 0
			self._dateFormat = ''

	def _getPeriod(self):
		return self._period
	period = property(_getPeriod, _setPeriod)
	
	def _useFile(self, filename):
		self._ensureDirectoryExists(filename)
		self.stream = open(filename, self.mode)

	def _ensureDirectoryExists(self, filename):
		dirname = os.path.dirname(filename)
		if dirname and not os.path.exists(dirname):
			os.makedirs(dirname)

	def getFilename(self, t):
		"""
		Return the appropriate filename for the given time
		based on the defined period.
		"""
		root, ext = os.path.splitext(self.baseFilename)
		# remove seconds not significant to the period
		if self._periodSeconds:
			t -= t % self._periodSeconds
		# convert it to a datetime object for formatting
		dt = datetime.datetime.utcfromtimestamp(t)
		# append the datestring to the filename
		# workaround for datetime.strftime not handling '' properly
		if not self._dateFormat == '':
			appendedDate = dt.strftime(self._dateFormat)
		else:
			appendedDate = ''
		if appendedDate:
			# in the future, it would be nice for this format
			#  to be supplied as a parameter.
			result = root + ' ' + appendedDate + ext
		else:
			result = self.baseFilename
		return result

	def emit(self, record):
		"""
		Emit a record.

		Output the record to the file, ensuring that the currently-
		opened file has the correct date.
		"""
		now = time.time()
		currentName = self.getFilename(now)
		try:
			if not self.stream.name == currentName:
				self._useFile(currentName)
		except AttributeError:
			# a stream has not been created, so create one.
			self._useFile(currentName)
		logging.StreamHandler.emit(self, record)

	def close(self):
		"""
		Closes the stream.
		"""
		try:
			self.stream.close()
		except AttributeError: pass

class LogFileWrapper(object):
	"""
	Emulates a file to replace stdout or stderr or
	anothe file object and redirects its output to
	a logger.
	
	Since data will often be send in partial lines or
	multiple lines, data is queued up until a new line
	is received.  Each line of text is send to the
	logger separately.
	"""
	def __init__(self, name, lvl = logging.DEBUG):
		self.logger = logging.getLogger(name)
		self.lvl = lvl
		self.queued = ''

	def write(self, data):
		data = self.queued + data
		data = string.split(data, '\n')
		for line in data[:-1]:
			self.logger.log(self.lvl, line)
		self.queued = data[-1]

class splitter(object):
	"""object that will split a string with the given arguments for each call
	>>> s = splitter(',')
	>>> s('hello, world, this is your, master calling')
	['hello', ' world', ' this is your', ' master calling']
"""
	def __init__(self, *args):
		self.args = args

	def __call__(self, s):
		return s.split(*self.args)

class ciString(str):
	"""A case insensitive string class; behaves just like str
	except compares equal when the only variation is case.
	>>> s = ciString('hello world')
	>>> s == 'Hello World'
	True
	>>> 'Hello World' == s
	True
	"""
	def __cmp__(self, other):
		return self.lower().__cmp__(other.lower())
	def __eq__(self, other):
		return self.lower() == other.lower()
	def __hash__(self):
		return hash(self.lower())
	# cache lower since it's likely to be called frequently.
	def lower(self):
		return self.__dict__.setdefault('_lower', str.lower(self))

class ciDict(dict):
	"""A case-insensitive dictionary (keys are compared as insensitive
	if they are strings.
	>>> d = ciDict()
	>>> d['heLlo'] = 'world'
	>>> d
	{'heLlo': 'world'}
	>>> d['hello']
	'world'
	>>> ciDict({'heLlo': 'world'})
	{'heLlo': 'world'}
	>>> d = ciDict({'heLlo': 'world'})
	>>> d['hello']
	'world'
	>>> d
	{'heLlo': 'world'}
	>>> d = ciDict({'heLlo': 'world', 'Hello': 'world'})
	>>> d
	{'heLlo': 'world'}
	"""
	def __setitem__(self, key, val):
		if isinstance(key, basestring):
			key = ciString(key)
		dict.__setitem__(self, key, val)

	def __init__(self, *args, **kargs):
		# build a dictionary using the default constructs
		d = dict(*args, **kargs)
		# build this dictionary using case insensitivity.
		map(self.__setitem__, d.keys(), d.values())

def randbytes(n):
	"Returns n random bytes"
	for i in xrange(n / 4):
		for byte in struct.pack('f', random.random()):
			yield byte
	for byte in struct.pack('f', random.random())[: n % 4]:
		yield byte

def flatten(l):
	"""flatten takes a list of lists and returns a single list with each element from the
	sublists.  For example,
	>>> flatten(['a','b',['c','d',['e','f'],'g'],'h']) == ['a','b','c','d','e','f','g','h']
	True
	"""
	if not isinstance(l, (list, tuple)):
		result = [l]
	elif filter(lambda x: isinstance(x, (list, tuple)), l):
		result = []
		map(result.extend, map(flatten, l))
	else:
		result = l
	return result

def readChunks(file, chunkSize = 2048, updateFunc = lambda x: None):
	"""Read file in chunks of size chunkSize (or smaller).
	If updateFunc is specified, call it on every chunk with the amount read."""
	while(1):
		res = file.read(chunkSize)
		if not res: break
		updateFunc(len(res))
		yield res

def binarySplit(seq, func = bool):
	"""Split a sequence into two sequences:  the first is elements that return
	True for func(element) and the second for False == func(element).
	By default, func = bool, so uses the truth value of the object."""
	queues = hashSplit(seq, func)
	return queues.getFirstNQueues(2)

class hashSplit(dict):
	"""Split a sequence into n sequences where n is determined by the number
	of distinct values returned by hash(func(element)) for each element in the sequence.
	>>> truthsplit = hashSplit(['Test', '', 30, None], bool)
	>>> trueItems = truthsplit[True]
	>>> falseItems = truthsplit[False]
	>>> tuple(falseItems)
	('', None)
	>>> tuple(trueItems)
	('Test', 30)
	>>> everyThirdSplit = hashSplit(xrange(99), lambda n: n%3)
	>>> zeros = everyThirdSplit[0]
	>>> ones = everyThirdSplit[1]
	>>> twos = everyThirdSplit[2]
	>>> zeros.next()
	0
	>>> zeros.next()
	3
	>>> ones.next()
	1
	>>> twos.next()
	2
	>>> ones.next()
	4
	"""
	def __init__(self, sequence, func = lambda x: x):
		self.sequence = iter(sequence)
		self.func = func

	def __getitem__(self, i):
		try:
			return dict.__getitem__(self, i)
		except KeyError:
			return self.__searchForItem__(i)

	def __getNext__(self):
		"get the next item from the sequence and queue it up"
		item = self.sequence.next()
		try:
			queue = dict.__getitem__(self, self.func(item))
		except KeyError:
			queue = iterQueue(self.__getNext__)
			self[self.func(item)] = queue
		queue.enqueue(item)

	def __searchForItem__(self, i):
		"search for the queue that would hold item i"
		try:
			self.__getNext__()
			return self[i]
		except StopIteration:
			return iter([])

	def getFirstNQueues(self, n):
		"""Run through the sequence until n queues are created and return
		them.  If fewer are created, return those plus empty iterables to
		compensate."""
		try:
			while len(self) < n:
				self.__getNext__()
		except StopIteration:
			pass
		createEmptyIterable = lambda x: iter([])
		return self.values() + map(createEmptyIterable, xrange(n - len(self)))

class iterQueue(object):
	def __init__(self, getNext):
		self.queued = []
		self.getNext = getNext

	def __iter__(self):
		return self

	def next(self):
		while not self.queued:
			self.getNext()
		return self.queued.pop()

	def enqueue(self, item):
		self.queued.insert(0, item)

class testSplit(hashSplit):
	def __init__(self, sequence):
		raise NotImplementedError, 'This class is just an idea.  Don\'t use it'
		self.sequence = iter(sequence)

	def __getitem__(self, test):
		try:
			return dict.__getitem__(self, test)
		except KeyError:
			return self.__searchForTest__(test)

	def __searchForTest__(self, test):
		"search for the queue that holds items that return true for test"
		try:
			self[test] = self.__getNext__()
			return self[test]
		except StopIteration:
			return iter([])

	def __getNext__(self):
		"get the next item from the sequence and queue it up"
		item = self.sequence.next()
		try:
			queue = dict.__getitem__(self, self.func(item))
		except KeyError:
			queue = iterQueue(self.__getNext__)
			self[self.func(item)] = queue
		queue.enqueue(item)


def ordinalth(n):
	"""Return the ordinal with 'st', 'th', or 'nd' appended as appropriate.
	>>> map(ordinalth, xrange(-5, 22))
	['-5th', '-4th', '-3rd', '-2nd', '-1st', '0th', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th', '13th', '14th', '15th', '16th', '17th', '18th', '19th', '20th', '21st']
	"""
	# zero through three map to 'th', 'st', 'nd', 'rd'
	t = ('th', 'st', 'nd', 'rd')
	# special case: ones digit is > 3
	ones = abs(n) % 10
	forceth = ones > 3
	# special case: n ends in 11, 12, 13
	forceth |= abs(n) % 100 in (11, 12, 13)
	index = [ones, 0][forceth]
	return '%d%s' % (n, t[index])

	