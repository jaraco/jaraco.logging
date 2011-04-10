from __future__ import absolute_import

import logging
import time
import warnings

from jaraco import dateutil

def add_options(parser):
	warnings.warn("add_options is deprecated. use add_arguments", DeprecationWarning)
	return add_arguments(parser)

def add_arguments(parser):
	"""
	Add arguments to an ArgumentParser or OptionParser for purposes of
	grabbing a logging level.
	"""
	adder = (
		getattr(parser, 'add_argument', None)
		or getattr(parser, 'add_option')
	)
	adder('-l', '--log-level', default='info',
		help="Set log level (DEBUG, INFO, WARNING, ERROR)")

def setup(options):
	"""
	Setup logging with options or arguments from an OptionParser or
	ArgumentParser
	"""
	logging.basicConfig(level=getattr(logging, options.log_level.upper()))

class TimestampFileHandler(logging.StreamHandler):
	"""
	A logging handler which will log to a file, similar to
	logging.handlers.RotatingFileHandler, but instead of
	appending a number, uses a timestamp to periodically select
	new file names to log to.
	
	Since this was developed, a TimedRotatingFileHandler was added to
	the Python stdlib. This class is still useful because it 
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
