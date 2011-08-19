# -*- coding: UTF-8 -*-

from __future__ import absolute_import, division

"""
jaraco.util:
  small functions or classes that don't have a home elsewhere
"""

__author__ = 'Jason R. Coombs <jaraco@jaraco.com>'
__version__ = '$Rev$'[6:-2]
__svnauthor__ = '$Author$'[9:-2]
__date__ = '$Date$'[7:-2]

import string
import urllib
import os
import sys
import re
import operator
import logging
import datetime
import codecs
import random
import itertools
from textwrap import dedent

log = logging.getLogger(__name__)

def trim(s):
	"""
	Trim something like a docstring to remove the whitespace that
	is common due to indentation and formatting.
	"""
	return dedent(s).strip()

def coerce_number(value):
	"""
	coerce_number takes a value and attempts to convert it to a float,
	or int.

	If none of the conversions are successful, the original value is
	returned.

	>>> coerce_number('3')
	3L

	>>> coerce_number('foo')
	'foo'
	"""
	result = value
	for transform in (float, long):
		try: result = transform(value)
		except ValueError: pass

	return result

def make_rows(num_columns, seq):
	"""
	Make a sequence into rows of num_columns columns
	>>> tuple(make_rows(2, [1, 2, 3, 4, 5]))
	((1, 4), (2, 5), (3, None))
	>>> tuple(make_rows(3, [1, 2, 3, 4, 5]))
	((1, 3, 5), (2, 4, None))
	"""
	# calculate the minimum number of rows necessary to fit the list in
	# num_columns Columns
	num_rows, partial = divmod(len(seq), num_columns)
	if partial:
		num_rows += 1
	# break the seq into num_columns of length num_rows
	from .itertools import grouper
	result = grouper(num_rows, seq)
	# result is now a list of columns... transpose it to return a list
	# of rows
	return zip(*result)

def grouper(size, seq):
	"""
	Take a sequence and break it up into chunks of the specified size.
	The last chunk may be smaller than size. `seq` must follow the
	0-indexed sequence protocol.

	This works very similar to jaraco.util.iter_.grouper_nofill, except
	it works with strings as well.

	>>> tuple(grouper(3, 'foobarbaz'))
	('foo', 'bar', 'baz')
	>>> tuple(grouper(42, []))
	()
	>>> tuple(grouper(3, list(range(10))))
	([0, 1, 2], [3, 4, 5], [6, 7, 8], [9])
	"""
	for i in range(0, len(seq), size):
		yield seq[i:i+size]

class Stopwatch(object):
	"""
	A simple stopwatch which starts automatically.

	>>> w = Stopwatch()
	>>> _1_sec = datetime.timedelta(seconds=1)
	>>> w.split() < _1_sec
	True
	>>> import time
	>>> time.sleep(1.0)
	>>> w.split() >= _1_sec
	True
	>>> w.stop() >= _1_sec
	True
	>>> w.reset()
	>>> w.start()
	>>> w.split() < _1_sec
	True
	"""
	def __init__(self):
		self.reset()
		self.start()

	def reset(self):
		self.elapsed = datetime.timedelta(0)
		if hasattr(self, 'start_time'):
			del self.start_time

	def start(self):
		self.start_time = datetime.datetime.now()

	def stop(self):
		stop_time = datetime.datetime.now()
		self.elapsed += stop_time - self.start_time
		del self.start_time
		return self.elapsed

	def split(self):
		local_duration = datetime.datetime.now() - self.start_time
		return self.elapsed + local_duration

def ReplaceList(object, substitutions):
	try:
		for old, new in substitutions:
			object = object.replace(old, new)
	except AttributeError:
		# object does not have a replace method
		pass
	return object

def ReverseLists(lists):
	"""
	>>> ReverseLists([[1,2,3], [4,5,6]])
	[[3, 2, 1], [6, 5, 4]]
	"""

	return list(map(list, map(reversed, lists)))

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

def randbytes(n):
	"Returns n random bytes"
	for i in range(n // 4):
		for byte in struct.pack('f', random.random()):
			yield byte
	for byte in struct.pack('f', random.random())[: n % 4]:
		yield byte

def readChunks(file, chunkSize = 2048, updateFunc = lambda x: None):
	"""Read file in chunks of size chunkSize (or smaller).
	If updateFunc is specified, call it on every chunk with the amount read."""
	while(1):
		res = file.read(chunkSize)
		if not res: break
		updateFunc(len(res))
		yield res

def bisect(seq, func = bool):
	"""
	Split a sequence into two sequences:  the first is elements that
	return True for func(element) and the second for False ==
	func(element).
	By default, func = bool, so uses the truth value of the object.
	"""
	queues = groupby_saved(seq, func)
	return queues.getFirstNQueues(2)

class groupby_saved(object):
	"""
	Split a sequence into n sequences where n is determined by the
	number of distinct values returned by a key function applied to each
	element in the sequence.

	>>> truthsplit = groupby_saved(['Test', '', 30, None], bool)
	>>> truthsplit['x']
	Traceback (most recent call last):
	...
	KeyError: 'x'
	>>> trueItems = truthsplit[True]
	>>> falseItems = truthsplit[False]
	>>> tuple(iter(falseItems))
	('', None)
	>>> tuple(iter(trueItems))
	('Test', 30)

	>>> everyThirdSplit = groupby_saved(range(99), lambda n: n%3)
	>>> zeros = everyThirdSplit[0]
	>>> ones = everyThirdSplit[1]
	>>> twos = everyThirdSplit[2]
	>>> next(zeros)
	0
	>>> next(zeros)
	3
	>>> next(ones)
	1
	>>> next(twos)
	2
	>>> next(ones)
	4
	"""
	def __init__(self, sequence, func = lambda x: x):
		self.sequence = iter(sequence)
		self.func = func
		self.queues = dict()

	def __getitem__(self, key):
		try:
			return self.queues[key]
		except KeyError:
			return self.__find_queue__(key)

	def __fetch__(self):
		"get the next item from the sequence and queue it up"
		item = next(self.sequence)
		key = self.func(item)
		queue = self.queues.setdefault(key, FetchingQueue(self.__fetch__))
		queue.enqueue(item)

	def __find_queue__(self, key):
		"search for the queue indexed by key"
		try:
			while not key in self.queues:
				self.__fetch__()
			return self.queues[key]
		except StopIteration:
			raise KeyError(key)

	def get_first_n_queues(self, n):
		"""
		Run through the sequence until n queues are created and return
		them. If fewer are created, return those plus empty iterables to
		compensate.
		"""
		try:
			while len(self.queues) < n:
				self.__fetch__()
		except StopIteration:
			pass
		empty_iter_factory = lambda: iter([])
		values = list(self.queues.values())
		missing = n - len(values)
		values.extend(iter([]) for n in range(missing))
		return values

class FetchingQueue(list):
	"""
	An attractive queue ... just kidding.

	A FIFO Queue that is supplied with a function to inject more into
	the queue if it is empty.

	>>> values = iter(xrange(10))
	>>> get_value = lambda: globals()['q'].enqueue(next(values))
	>>> q = FetchingQueue(get_value)
	>>> [x for x in q] == range(10)
	True

	Note that tuple(q) or list(q) would not have worked above because
	tuple(q) just copies the elements in the list (of which there are
	none).
	"""
	def __init__(self, fetcher):
		self._fetcher = fetcher

	def next(self):
		while not self:
			self._fetcher()
		return self.pop()

	def __iter__(self):
		while True:
			yield next(self)

	def enqueue(self, item):
		self.insert(0, item)

def ordinalth(n):
	"""Return the ordinal with 'st', 'th', or 'nd' appended as appropriate.
	>>> list(map(ordinalth, range(-5, 22)))
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

class PasswordGenerator(object):
	"""
	Generates random passwords
	>>> pw = PasswordGenerator.make_password(8, encoding=None)
	>>> len(pw)
	8
	>>> pw != PasswordGenerator.make_password(8, encoding=None)
	True
	"""

	@staticmethod
	def make_password(n_bytes = 8, encoding = 'base-64'):
		'Make a password with n_bytes of disorder; optionally encoded'
		chars = PasswordGenerator.get_random_chars(n_bytes)
		result = ''.join(chars)
		null_encoder = lambda s: (s, len(s))
		encoder = codecs.getencoder(encoding) if encoding else null_encoder
		encoded, length = encoder(result)
		return encoded

	@staticmethod
	def get_random_chars(len):
		return itertools.islice(PasswordGenerator.random_byte_generator(), len)

	@staticmethod
	def random_byte_generator():
		while True:
			yield chr(random.randint(0, 255))

callable = lambda obj: hasattr(obj, '__call__')
